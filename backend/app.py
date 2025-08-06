from flask import Flask, request, jsonify, send_from_directory,abort
from flask_cors import CORS
import numpy as np
import json
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import re
import os 
import logging 
import traceback

app = Flask(__name__)

# Configure CORS to only allow requests from your Vercel frontend
ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, resources={
    r"/*": {  # Changed from /api/* to /* to allow all routes
        "origins": ALLOWED_ORIGINS,
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

backend_dir = os.path.dirname(os.path.abspath(__file__))

# Load preprocessed data
vectors_path = os.path.join(backend_dir, 'vectors.npy')
solutions_path = os.path.join(backend_dir, 'updated_solutions.json')
labels_path = os.path.join(backend_dir, 'kmeans_labels.npy')
questions_path = os.path.join(backend_dir, 'all_leetcode_questions_text.json')

# Load preprocessed data
vectors = np.load(vectors_path)
with open(solutions_path) as f:
    solutions_dict = json.load(f)
labels = np.load(labels_path)
with open(questions_path) as f:
    questions_dict = json.load(f)

# Create a reverse mapping from vector indices to problem names
index_to_problem = []
for problem, data in solutions_dict.items():
    index_to_problem.extend([problem] * len(data['solutions']))

def extract_problem_name(input_str):
    url_pattern = re.compile(r'https?://leetcode.com/problems/([a-z0-9-]+)/?.*')
    match = url_pattern.match(input_str)
    if match:
        return match.group(1)
    return input_str.replace(' ', '-').lower()

@app.route('/api/similar_problems', methods=['POST'])
def similar_problems():
    try:
        data = request.json
        raw_input = data['problem_name']
        problem_name = extract_problem_name(raw_input)

        logger.info(f'Processing problem: {problem_name}')

        # Find the index of the problem in solutions_dict
        if problem_name not in solutions_dict:
            abort(404, description="Problem not found")

        problem_index = next((i for i, problem in enumerate(index_to_problem) if problem == problem_name), None)
        if problem_index is None:
            abort(404, description="Problem not found")

        # Compute cosine similarity
        similarities = cosine_similarity([vectors[problem_index]], vectors).flatten()
        scaler = MinMaxScaler()
        normalized_similarities = scaler.fit_transform(similarities.reshape(-1, 1)).flatten()

        # Get indices of top 10 most similar problems
        similar_indices = normalized_similarities.argsort()[-11:-1][::-1]

        # Calculate the number of unique problems with similarity >= 0.97
        unique_problems = {index_to_problem[i] for i, similarity in enumerate(similarities) if similarity >= 0.99}
        extremely_similar_count = len(unique_problems)

        # Fetch similar problem names, their links, difficulty, and tags
        similar_problems = [
            {
                "name": index_to_problem[i].replace('-', ' ').title(),
                "link": f"https://leetcode.com/problems/{index_to_problem[i]}/",
                "similarity_score": round(float(normalized_similarities[i] * 100), 2),
                "difficulty": solutions_dict[index_to_problem[i]]['difficulty'],
                "tags": solutions_dict[index_to_problem[i]]['tags']
            } for i in similar_indices
        ]

        question_content = questions_dict.get(problem_name, '')

        response_data = {
            "problem_name": problem_name.replace('-', ' ').title(),
            "question_content": question_content,
            "difficulty": solutions_dict[problem_name]['difficulty'],
            "tags": solutions_dict[problem_name]['tags'],
            "extremely_similar_count": str(extremely_similar_count),
            "similar_problems": similar_problems
        }

        response = jsonify(response_data)
        return response
    except Exception as e:
        logger.error(f"Error in /similar_problems: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

# Add root route handler
@app.route('/')
def root():
    return jsonify({
        "status": "online",
        "message": "Leetcode Matchmaker API is running",
        "endpoints": {
            "/api/similar_problems": "POST - Find similar Leetcode problems",
            "/api/health": "GET - Health check"
        }
    })

# Add health check endpoint
@app.route('/api/health')
def health():
    return jsonify({"status": "healthy"})

# Required for Vercel
app.debug = True

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
