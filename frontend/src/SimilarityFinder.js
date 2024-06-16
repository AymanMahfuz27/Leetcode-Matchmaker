// src/SimilarityFinder.js
import React, { useState } from 'react';
import axios from 'axios';

const SimilarityFinder = () => {
  const [problemName, setProblemName] = useState('');
  const [similarProblems, setSimilarProblems] = useState([]);
  const [error, setError] = useState('');

  const handleSearch = async () => {
    try {
      const response = await axios.post('http://localhost:5000/similar_problems', { problem_name: problemName });
      setSimilarProblems(response.data);
      setError('');
    } catch (error) {
      console.error('Error fetching similar problems', error);
      setError('Error fetching similar problems');
      setSimilarProblems([]);
    }
  };

  return (
    <div>
      <h1>LeetCode Problem Similarity Finder</h1>
      <input
        type="text"
        value={problemName}
        onChange={(e) => setProblemName(e.target.value)}
        placeholder="Enter LeetCode problem name"
      />
      <button onClick={handleSearch}>Search</button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <ul>
        {similarProblems.map((problem, index) => (
          <li key={index}>{problem}</li>
        ))}
      </ul>
    </div>
  );
};

export default SimilarityFinder;
