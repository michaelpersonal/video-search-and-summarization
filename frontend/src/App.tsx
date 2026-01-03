import React, { useState, useEffect } from 'react';
import CameraCapture from './components/CameraCapture';
import SearchResults from './components/SearchResults';
import { SearchResult, HealthCheck } from './types';
import apiService from './services/api';
import './App.css';

function App() {
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedResult, setSelectedResult] = useState<SearchResult | null>(null);
  const [healthStatus, setHealthStatus] = useState<HealthCheck | null>(null);

  // Helper function to construct image URL
  const getImageUrl = (imagePath: string) => {
    if (imagePath.startsWith('images/')) {
      return `http://localhost:8000/${imagePath}`;
    } else {
      return `http://localhost:8000/uploads/${imagePath}`;
    }
  };

  useEffect(() => {
    // Check API health on component mount
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const health = await apiService.getHealth();
      setHealthStatus(health);
    } catch (error) {
      console.error('Health check failed:', error);
      setHealthStatus({
        status: 'unhealthy',
        ai_model_available: false,
        timestamp: new Date().toISOString()
      });
    }
  };

  const handleImageCapture = async (file: File) => {
    setIsLoading(true);
    setError(null);
    setSearchResults([]);
    setSelectedResult(null);

    try {
      const response = await apiService.uploadImage(file);
      setSearchResults(response.search_results);
    } catch (error: any) {
      console.error('Error uploading image:', error);
      setError(error.response?.data?.detail || 'Failed to analyze image. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleError = (errorMessage: string) => {
    setError(errorMessage);
  };

  const handleSelectResult = (result: SearchResult) => {
    setSelectedResult(result);
  };

  const handleCloseDetail = () => {
    setSelectedResult(null);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🔧 Spare Parts ID System</h1>
        <p>AI-powered spare parts identification</p>
        
        {healthStatus && (
          <div className="health-status">
            <span className={`status ${healthStatus.status}`}>
              {healthStatus.status === 'healthy' ? '🟢' : '🔴'} API: {healthStatus.status}
            </span>
            <span className={`ai-status ${healthStatus.ai_model_available ? 'available' : 'unavailable'}`}>
              {healthStatus.ai_model_available ? '🤖' : '⚠️'} AI: {healthStatus.ai_model_available ? 'Available' : 'Unavailable'}
            </span>
          </div>
        )}
      </header>

      <main className="App-main">
        {error && (
          <div className="error-message">
            <span>❌ {error}</span>
            <button onClick={() => setError(null)}>✕</button>
          </div>
        )}

        <CameraCapture 
          onImageCapture={handleImageCapture}
          onError={handleError}
        />

        <SearchResults
          results={searchResults}
          isLoading={isLoading}
          onSelectResult={handleSelectResult}
        />

        {selectedResult && (
          <div className="detail-modal">
            <div className="modal-content">
              <button className="close-button" onClick={handleCloseDetail}>
                ✕
              </button>
              
              <div className="detail-header">
                <h2>{selectedResult.spare_part.material_number}</h2>
                <span className="confidence-badge">
                  {Math.round(selectedResult.confidence_score * 100)}% match
                </span>
              </div>

              <div className="detail-body">
                <div className="detail-image">
                  {selectedResult.spare_part.image_path ? (
                    <img 
                      src={getImageUrl(selectedResult.spare_part.image_path)}
                      alt={selectedResult.spare_part.description}
                    />
                  ) : (
                    <div className="placeholder-image">📦</div>
                  )}
                </div>

                <div className="detail-info">
                  <h3>Description</h3>
                  <p>{selectedResult.spare_part.description}</p>
                  
                  {selectedResult.spare_part.category && (
                    <>
                      <h3>Category</h3>
                      <p>{selectedResult.spare_part.category}</p>
                    </>
                  )}
                  
                  {selectedResult.spare_part.manufacturer && (
                    <>
                      <h3>Manufacturer</h3>
                      <p>{selectedResult.spare_part.manufacturer}</p>
                    </>
                  )}
                  
                  {selectedResult.spare_part.specifications && (
                    <>
                      <h3>Specifications</h3>
                      <p>{selectedResult.spare_part.specifications}</p>
                    </>
                  )}
                  
                  <h3>Match Reason</h3>
                  <p>{selectedResult.match_reason}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="App-footer">
        <p>© 2024 SCS Spare Parts Identification System</p>
      </footer>
    </div>
  );
}

export default App; 