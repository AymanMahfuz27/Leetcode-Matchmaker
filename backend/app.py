from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import json
from sklearn.metrics.pairwise import cosine_similarity
import re

app = Flask(__name__)
CORS(app)  # Enable CORS

# Load preprocessed data
vectors = np.load('vectors.npy')
with open('solutions.json') as f:
    solutions_dict = json.load(f)
labels = np.load('kmeans_labels.npy')

# Create a reverse mapping from vector indices to problem names
index_to_problem = []
for problem, solutions in solutions_dict.items():
    index_to_problem.extend([problem] * len(solutions))

def extract_problem_name(input_str):
    url_pattern = re.compile(r'https?://leetcode.com/problems/([a-z0-9-]+)/?.*')
    match = url_pattern.match(input_str)
    if match:
        return match.group(1)
    return input_str.replace(' ', '-').lower()

@app.route('/similar_problems', methods=['POST'])
def similar_problems():
    data = request.json
    raw_input = data['problem_name']
    problem_name = extract_problem_name(raw_input)
    
    # Find the index of the problem in solutions_dict
    if problem_name not in solutions_dict:
        return jsonify({"error": "Problem not found"}), 404

    problem_index = next((i for i, problem in enumerate(index_to_problem) if problem == problem_name), None)

    # Compute cosine similarity
    similarities = cosine_similarity([vectors[problem_index]], vectors).flatten()
    
    # Get indices of top 10 most similar problems
    similar_indices = similarities.argsort()[-11:-1][::-1]
    
    # Fetch similar problem names and their links
    similar_problems = [
        {
            "name": index_to_problem[i].replace('-', ' ').title(),
            "link": f"https://leetcode.com/problems/{index_to_problem[i]}/",
            "similarity_score": f'{similarities[i]}'
        } for i in similar_indices
    ]
    
    return jsonify(similar_problems)

if __name__ == '__main__':
    app.run(debug=True)