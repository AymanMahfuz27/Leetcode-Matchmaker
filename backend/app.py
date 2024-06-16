from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import json
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
CORS(app)

# Load preprocessed data
vectors = np.load('vectors.npy')
with open('solutions.json') as f:
    solutions = json.load(f)
labels = np.load('kmeans_labels.npy')

@app.route('/similar_problems', methods=['POST'])
def similar_problems():
    data = request.json
    problem_name = data['problem_name']
    
    # Find the index of the problem in solutions
    problem_index = next((i for i, sol in enumerate(solutions) if problem_name in sol), None)
    
    if problem_index is None:
        return jsonify({"error": "Problem not found"}), 404

    # Compute cosine similarity
    similarities = cosine_similarity([vectors[problem_index]], vectors).flatten()
    
    # Get indices of top 10 most similar problems
    similar_indices = similarities.argsort()[-11:-1][::-1]
    
    # Fetch similar problem names
    similar_problems = [solutions[i][:50] + '...' for i in similar_indices]
    
    return jsonify(similar_problems)

if __name__ == '__main__':
    app.run(debug=True)
