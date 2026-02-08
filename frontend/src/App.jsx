import React, { useState } from 'react';
import './App.css';
import axios from 'axios';

// Use relative URL in production, absolute in development
const API_URL = process.env.REACT_APP_API_URL || 
  (process.env.NODE_ENV === 'production' ? '' : 'http://localhost:8000');

function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await axios.post(`${API_URL}/ask`, {
        query: query.trim()
      });
      setResponse(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getActionColor = (action) => {
    switch (action) {
      case 'answer':
        return '#10b981';
      case 'escalate':
        return '#ef4444';
      case 'clarify':
        return '#f59e0b';
      case 'flag':
        return '#8b5cf6';
      default:
        return '#6b7280';
    }
  };

  const getActionIcon = (action) => {
    switch (action) {
      case 'answer':
        return '✓';
      case 'escalate':
        return '⚠';
      case 'clarify':
        return '?';
      case 'flag':
        return '🚩';
      default:
        return '•';
    }
  };

  return (
    <div className="App">
      <div className="container">
        <header className="header">
          <h1>🤖 Agentic RAG AI</h1>
          <p className="subtitle">Enterprise AI Assistant with Multi-Agent Reasoning</p>
        </header>

        <div className="main-content">
          <form onSubmit={handleSubmit} className="query-form">
            <div className="input-group">
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask a question about policies, procedures, or compliance..."
                className="query-input"
                rows="4"
                disabled={loading}
              />
              <button
                type="submit"
                className="submit-btn"
                disabled={loading || !query.trim()}
              >
                {loading ? 'Processing...' : 'Ask'}
              </button>
            </div>
          </form>

          {error && (
            <div className="error-box">
              <h3>Error</h3>
              <p>{error}</p>
            </div>
          )}

          {response && (
            <div className="response-box">
              <div className="response-header">
                <div
                  className="action-badge"
                  style={{ backgroundColor: getActionColor(response.action) }}
                >
                  <span className="action-icon">{getActionIcon(response.action)}</span>
                  <span className="action-text">{response.action.toUpperCase()}</span>
                </div>
              </div>

              <div className="response-content">
                <div className="message-section">
                  <h3>Response</h3>
                  <p className="message-text">{response.message}</p>
                </div>

                {response.flagged_documents && response.flagged_documents.length > 0 && (
                  <div className="flagged-section">
                    <h3>⚠️ Flagged Documents</h3>
                    <ul className="flagged-list">
                      {response.flagged_documents.map((doc, idx) => (
                        <li key={idx}>{doc}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          <div className="info-section">
            <h3>How it works</h3>
            <div className="flow-diagram">
              <div className="flow-step">
                <div className="step-number">1</div>
                <div className="step-text">Planner analyzes intent & risk</div>
              </div>
              <div className="flow-arrow">→</div>
              <div className="flow-step">
                <div className="step-number">2</div>
                <div className="step-text">RAG retrieves knowledge</div>
              </div>
              <div className="flow-arrow">→</div>
              <div className="flow-step">
                <div className="step-number">3</div>
                <div className="step-text">Evaluator checks confidence</div>
              </div>
              <div className="flow-arrow">→</div>
              <div className="flow-step">
                <div className="step-number">4</div>
                <div className="step-text">Debate or Direct response</div>
              </div>
              <div className="flow-arrow">→</div>
              <div className="flow-step">
                <div className="step-number">5</div>
                <div className="step-text">Final recommendation</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
