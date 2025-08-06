import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './SimilarityFinder.css';

const API_URL = process.env.REACT_APP_API_URL || 'https://leetcode-matchmaker-2bb8b1daa393.herokuapp.com';

const QuestionCard = ({ problemName, questionContent, difficulty, tags, extremelySimilarCount }) => {
  return (
    <div className="question-card">
      <h2>{problemName}</h2>
      <div className="extremely-similar-count">
        <span>Number of extremely similar questions: <strong><u>{extremelySimilarCount}</u></strong></span>
        <div className="tooltip">
          <span>ℹ️</span>
          <div className="tooltiptext">
            The count of extremely similar questions is determined based on a cosine similarity score of 0.99 or higher.
          </div>
        </div>
      </div>
      <p className={`difficulty ${difficulty.toLowerCase()}`}>{difficulty}</p>
      <div className="tags">
        {tags.map((tag, index) => (
          <span key={index} className="tag">
            {tag}
          </span>
        ))}
      </div>
      <div className="question-content" dangerouslySetInnerHTML={{ __html: questionContent }} />
    </div>
  );
};

const SimilarityFinder = () => {
  const [inputValue, setInputValue] = useState('');
  const [similarProblems, setSimilarProblems] = useState([]);
  const [displayedProblems, setDisplayedProblems] = useState([]);
  const [error, setError] = useState('');
  const [questionData, setQuestionData] = useState(null);  // New state for question data
  const problemsPerPage = 10;

  useEffect(() => {
    if (similarProblems.length > 0) {
      document.body.style.paddingTop = '100px';
      setDisplayedProblems(similarProblems.slice(0, problemsPerPage));
    } else {
      document.body.style.paddingTop = '0';
    }
  }, [similarProblems]);

  const handleSearch = async () => {
    if (!inputValue.trim()) return;
    try {
      const response = await axios.post(`${API_URL}/api/similar_problems`, { problem_name: inputValue });
      console.log('Response Data:', response.data);
  
      setSimilarProblems(response.data.similar_problems);
      setQuestionData({
        problem_name: response.data.problem_name,
        question_content: response.data.question_content,
        difficulty: response.data.difficulty,
        tags: response.data.tags,
        extremely_similar_count: response.data.extremely_similar_count,
      });
      setError('');
    } catch (error) {
      console.error('Error fetching similar problems', error);
      if (error.response) {
        setError(error.response.data.error);
      } else {
        setError('Error fetching similar problems');
      }
      setSimilarProblems([]);
      setDisplayedProblems([]);
    }
  };
  
  const handleKeyPress = (event) => {
    if (event.key === 'Enter') {
      handleSearch();
    }
  };

  const getSimilarityCategory = (score) => {
    const s = parseFloat(score);
    if (s >= 95) return 'Extremely Similar';
    if (s >= 85) return 'Very Similar';
    if (s >= 70) return 'Similar';
    if (s >= 50) return 'Somewhat Similar';
    return 'Less Similar';
  };

  // const loadMore = () => {
  //   const nextPage = currentPage + 1;
  //   const newDisplayedProblems = similarProblems.slice(0, problemsPerPage * nextPage);
  //   setDisplayedProblems(newDisplayedProblems);
  //   setCurrentPage(nextPage);
  // };

  return (
    <div className={`container ${!questionData ? 'centered-container' : ''}`}>
      <h1 className="title">LeetCode Problem Similarity Finder</h1>
      <div className="search-container">
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
      </div>
      {error && <p className="error-message">{error}</p>}
      <div className="similarity-finder">
        {questionData && (
          <QuestionCard
            problemName={questionData.problem_name}
            questionContent={questionData.question_content}
            difficulty={questionData.difficulty}
            tags={questionData.tags}
            extremelySimilarCount={questionData.extremely_similar_count}
          />
        )}
        {displayedProblems.length > 0 && (
          <>
          <table className="results-table">
            <caption>Similar Problems</caption>
            <thead>
              <tr>
                <th>Problem</th>
                <th>Tags</th>
                <th>Difficulty</th>
                <th>Similarity Score</th>
              </tr>
            </thead>
            <tbody>
              {displayedProblems.map((problem, index) => (
                <tr key={index}>
                  <td className='left-align'>
                    <a
                      href={problem.link}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {problem.name}
                    </a>
                  </td>
                  <td>
                    {problem.tags.map((tag, tagIndex) => (
                      <span key={tagIndex} className="tag">
                        {tag}
                      </span>
                    ))}
                  </td>
                  <td>
                    <span className={`difficulty ${problem.difficulty.toLowerCase()}`}>
                      {problem.difficulty}
                    </span>
                  </td>
                  <td>{problem.similarity_score}% ({getSimilarityCategory(problem.similarity_score)})</td>
                </tr>
              ))}
            </tbody>
          </table>
          </>
        )}
      </div>
      <footer className="footer">
        This project helps you find LeetCode problems similar to the one you searched for by using cosine similarity on problem vectors.
      </footer>
    </div>
  );
};

export default SimilarityFinder;
