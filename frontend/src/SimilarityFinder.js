import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './SimilarityFinder.css';
import QuestionCard from './QuestionCard';  // Import the new component


const SimilarityFinder = () => {
  const [inputValue, setInputValue] = useState('');
  const [similarProblems, setSimilarProblems] = useState([]);
  const [displayedProblems, setDisplayedProblems] = useState([]);
  const [error, setError] = useState('');
  // const [currentPage, setCurrentPage] = useState(1);
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

  // const handleSearch = async () => {
  //   if (!inputValue.trim()) return;
  //   try {
  //     const response = await axios.post('/similar_problems', { problem_name: inputValue });

  //     setSimilarProblems(response.data);
  //     setQuestionData(response.data);  // Set the question data
  //     setError('');
  //     setCurrentPage(1);
  //     setDisplayedProblems(response.data.slice(0, problemsPerPage));
  //   } catch (error) {
  //     console.error('Error fetching similar problems', error);
  //     if (error.response) {
  //       setError(error.response.data.error);
  //     } else {
  //       setError('Error fetching similar problems');
  //     }
  //     setSimilarProblems([]);
  //     setDisplayedProblems([]);
  //   }
  // };


  const handleSearch = async () => {
    if (!inputValue.trim()) return;
    try {
      const response = await axios.post('/similar_problems', { problem_name: inputValue });
      console.log('Response Data:', response.data); // Log the response data to see its structure
  
      // Assuming response.data contains the expected structure
      setSimilarProblems(response.data.similar_problems);
      setQuestionData({
        problem_name: response.data.problem_name,
        question_content: response.data.question_content,
        difficulty: response.data.difficulty,
        tags: response.data.tags,
        extremely_similar_count: response.data.extremely_similar_count,
      });  // Set the question data
      setError('');
      // setCurrentPage(1);
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

  // const loadMore = () => {
  //   const nextPage = currentPage + 1;
  //   const newDisplayedProblems = similarProblems.slice(0, problemsPerPage * nextPage);
  //   setDisplayedProblems(newDisplayedProblems);
  //   setCurrentPage(nextPage);
  // };

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
      {questionData && (  // Display the question card if question data is available
        <QuestionCard 
          problemName={questionData.problem_name}
          questionContent={questionData.question_content}
          difficulty={questionData.difficulty}
          tags={questionData.tags}
          extremelySimilarCount={questionData.extremely_similar_count}
        />
      )}
      {/* <h2 className="title">Similar Problems</h2> */}
      {displayedProblems.length > 0 && (
        <>
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
              {displayedProblems.map((problem, index) => (
                <tr key={index} >
                  <td className = 'left-align'>
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
                  <td>{problem.similarity_score}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {/* {displayedProblems.length < similarProblems.length && (
            <button onClick={loadMore} className="load-more-button">
              Load More
            </button>
          )} */}
        </>
      )}
      <footer className="footer">
        This project helps you find LeetCode problems similar to the one you searched for by using cosine similarity on problem vectors.
      </footer>
    </div>
  );
};

export default SimilarityFinder;
