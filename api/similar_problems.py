from http.server import BaseHTTPRequestHandler
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import os
import re

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            raw_input = data.get('problem_name')
            if not raw_input:
                self._send_error("Problem name is required")
                return
                
            problem_name = self._extract_problem_name(raw_input)
            
            # Load data files
            backend_dir = os.path.dirname(os.path.abspath(__file__))
            vectors = np.load(os.path.join(backend_dir, 'vectors.npy'))
            with open(os.path.join(backend_dir, 'updated_solutions.json')) as f:
                solutions_dict = json.load(f)
            with open(os.path.join(backend_dir, 'all_leetcode_questions_text.json')) as f:
                questions_dict = json.load(f)
                
            # Find problem index
            if problem_name not in solutions_dict:
                self._send_error("Problem not found")
                return
                
            # Create index mapping
            index_to_problem = []
            for prob, data in solutions_dict.items():
                index_to_problem.extend([prob] * len(data['solutions']))
                
            problem_index = next((i for i, prob in enumerate(index_to_problem) if prob == problem_name), None)
            if problem_index is None:
                self._send_error("Problem not found")
                return
                
            # Compute similarities
            similarities = cosine_similarity([vectors[problem_index]], vectors).flatten()
            scaler = MinMaxScaler()
            normalized_similarities = scaler.fit_transform(similarities.reshape(-1, 1)).flatten()
            
            # Get top similar problems
            similar_indices = normalized_similarities.argsort()[-11:-1][::-1]
            
            # Get extremely similar count
            unique_problems = {index_to_problem[i] for i, similarity in enumerate(similarities) if similarity >= 0.99}
            extremely_similar_count = len(unique_problems)
            
            # Format response
            similar_problems = [
                {
                    "name": index_to_problem[i].replace('-', ' ').title(),
                    "link": f"https://leetcode.com/problems/{index_to_problem[i]}/",
                    "similarity_score": f'{str(similarities[i])[0:5]}',
                    "difficulty": solutions_dict[index_to_problem[i]]['difficulty'],
                    "tags": solutions_dict[index_to_problem[i]]['tags']
                } for i in similar_indices
            ]
            
            response_data = {
                "problem_name": problem_name.replace('-', ' ').title(),
                "question_content": questions_dict.get(problem_name, ''),
                "difficulty": solutions_dict[problem_name]['difficulty'],
                "tags": solutions_dict[problem_name]['tags'],
                "extremely_similar_count": str(extremely_similar_count),
                "similar_problems": similar_problems
            }
            
            self._send_response(response_data)
            
        except Exception as e:
            self._send_error(f"Internal server error: {str(e)}")
    
    def _extract_problem_name(self, input_str):
        url_pattern = re.compile(r'https?://leetcode.com/problems/([a-z0-9-]+)/?.*')
        match = url_pattern.match(input_str)
        if match:
            return match.group(1)
        return input_str.replace(' ', '-').lower()
    
    def _send_response(self, data):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def _send_error(self, message, status=400):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode()) 