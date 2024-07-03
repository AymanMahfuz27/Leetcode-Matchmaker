from flask import Flask, request, jsonify, send_from_directory,abort
from flask_cors import CORS
import numpy as np
import json
from sklearn.metrics.pairwise import cosine_similarity
import re
import os 
import logging 
import traceback

app = Flask(__name__, static_folder='../frontend/build', static_url_path='')
CORS(app, resources={r"/similar_problems": {"origins": "*"}})


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

@app.route('/similar_problems', methods=['POST'])
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

        # Get indices of top 10 most similar problems
        similar_indices = similarities.argsort()[-11:-1][::-1]
        unique_problems = {index_to_problem[i] for i, similarity in enumerate(similarities) if similarity >= 0.99}
        extremely_similar_count = len(unique_problems)

        # Fetch similar problem names, their links, difficulty, and tags
        similar_problems = [
            {
                "name": index_to_problem[i].replace('-', ' ').title(),
                "link": f"https://leetcode.com/problems/{index_to_problem[i]}/",
                "similarity_score": f'{str(similarities[i])[0:5]}',
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

        # logger.info(f'Response data: {response_data}')
        # for key, value in response_data.items():
        #     data_type = str(type(value))
        #     logger.info(f'{key} Datatype: {data_type}')
        
        response = jsonify(response_data)
        # response.headers.add("Access-Control-Allow-Origin", "https://leetcode-matchmaker.netlify.app")
        # response.headers.add("Access-Control-Allow-Headers", "Content-Type")
        # response.headers.add("Access-Control-Allow-Methods", "POST, OPTIONS")
        return response
    except Exception as e:
        logger.error(f"Error in /similar_problems: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


    


@app.route('/')
def serve():
    app.logger.info('Serving index.html')
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    app.logger.info(f'Serving static file: {path}')
    return send_from_directory(app.static_folder, path)


if __name__ == '__main__':
    app.run()
