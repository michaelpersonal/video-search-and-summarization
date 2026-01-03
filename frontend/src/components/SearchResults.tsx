import React from 'react';
import { SearchResult } from '../types';
import './SearchResults.css';

interface SearchResultsProps {
  results: SearchResult[];
  isLoading: boolean;
  onSelectResult: (result: SearchResult) => void;
}

const SearchResults: React.FC<SearchResultsProps> = ({ 
  results, 
  isLoading, 
  onSelectResult 
}) => {
  // Helper function to construct image URL
  const getImageUrl = (imagePath: string) => {
    if (imagePath.startsWith('images/')) {
      return `http://localhost:8000/${imagePath}`;
    } else {
      return `http://localhost:8000/uploads/${imagePath}`;
    }
  };

  if (isLoading) {
    return (
      <div className="search-results loading">
        <div className="loading-spinner">🔄</div>
        <p>Analyzing image...</p>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="search-results empty">
        <div className="empty-icon">🔍</div>
        <h3>No matches found</h3>
        <p>Try taking a clearer photo or uploading a different image.</p>
      </div>
    );
  }

  return (
    <div className="search-results">
      <h3>Potential Matches ({results.length})</h3>
      {results.length > 1 && (
        <div className="match-notice">
          <p>⚠️ Multiple close matches found. Please select the correct one:</p>
        </div>
      )}
      <div className="results-grid">
        {results.map((result, index) => (
          <div 
            key={result.spare_part.id} 
            className={`result-card ${index === 0 ? 'top-match' : ''}`}
            onClick={() => onSelectResult(result)}
          >
            {index === 0 && (
              <div className="top-match-badge">🥇 Best Match</div>
            )}
            <div className="result-image">
              {result.spare_part.image_path ? (
                <img 
                  src={getImageUrl(result.spare_part.image_path)}
                  alt={result.spare_part.description}
                  onError={(e) => {
                    const target = e.currentTarget as HTMLImageElement;
                    target.style.display = 'none';
                    const placeholder = target.nextElementSibling as HTMLElement;
                    if (placeholder) {
                      placeholder.style.display = 'block';
                    }
                  }}
                />
              ) : null}
              <div className="placeholder-image">📦</div>
            </div>
            
            <div className="result-info">
              <h4 className="material-number">
                {result.spare_part.material_number}
              </h4>
              <p className="description">
                {result.spare_part.description}
              </p>
              {result.spare_part.category && (
                <span className="category">
                  {result.spare_part.category}
                </span>
              )}
              <div className="confidence">
                <div className="confidence-bar">
                  <div 
                    className="confidence-fill"
                    style={{ width: `${result.confidence_score * 100}%` }}
                  ></div>
                </div>
                <span className="confidence-text">
                  {Math.round(result.confidence_score * 100)}% match
                </span>
              </div>
              <p className="match-reason">
                {result.match_reason}
              </p>
              <button className="select-button">
                Select This Match
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SearchResults; 