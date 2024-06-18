import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './SimilarityFinder.css';

const SimilarityFinder = () => {
  const [inputValue, setInputValue] = useState('');
  const [similarProblems, setSimilarProblems] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    if (similarProblems.length > 0) {
      document.body.style.paddingTop = '100px';
    } else {
      document.body.style.paddingTop = '0';
    }
  }, [similarProblems]);

  const handleSearch = async () => {
    if (!inputValue.trim()) return;
    try {
      const response = await axios.post(
        'http://localhost:5000/similar_problems',
        { problem_name: inputValue }
      );
      setSimilarProblems(response.data);
      setError('');
    } catch (error) {
      console.error('Error fetching similar problems', error);
      if (error.response) {
        setError(error.response.data.error);
      } else {
        setError('Error fetching similar problems');
      }
      setSimilarProblems([]);
    }
  };

  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="similarity-finder">
      <h1 className="title">LeetCode Problem Similarity Finder</h1>
      <input
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        placeholder="Enter LeetCode problem name or URL"
        onKeyPress={handleKeyPress}
        className="search-bar"
      />
      <button onClick={handleSearch} className="search-button">
        Search
      </button>
      {error && <p className="error-message">{error}</p>}
      {similarProblems.length > 0 && (
        <table className="results-table">
          <thead>
            <tr>
              <th>Problem</th>
              <th>Tags</th>
              <th>Difficulty</th>
              <th>Similarity Score</th>
            </tr>
          </thead>
          <tbody>
            {similarProblems.map((problem, index) => (
              <tr key={index}>
                <td>
                  <a
                    href={problem.link}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    {problem.name}
                  </a>
                </td>
                <td>{problem.tags.join(', ')}</td>
                <td>{problem.difficulty}</td>
                <td>{problem.similarity_score}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default SimilarityFinder;
