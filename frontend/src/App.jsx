import { useState } from 'react'
import './App.css'

function App() {
  const [code, setCode] = useState('')
  const [language, setLanguage] = useState('python')
  const [docType, setDocType] = useState('function')
  const [documentation, setDocumentation] = useState('')
  const [loading, setLoading] = useState(false)

  const generateDocs = async () => {
    if (!code.trim()) {
      alert('Please enter some code first!')
      return
    }

    setLoading(true)
    setDocumentation('')
    
    try {
      const response = await fetch('http://localhost:8000/generate-docs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          code: code, 
          language: language, 
          doc_type: docType 
        })
      })
      
      if (!response.ok) {
        throw new Error('Failed to generate documentation')
      }
      
      const data = await response.json()
      setDocumentation(data.documentation)
    } catch (error) {
      console.error('Error:', error)
      setDocumentation('Error: ' + error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="App">
      <header>
        <h1>🤖 AI Code Documentation Generator</h1>
        <p>Powered by Advanced Prompt Engineering</p>
      </header>
      
      <div className="controls">
        <div className="control-group">
          <label>Language:</label>
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            <option value="python">Python</option>
            <option value="javascript">JavaScript</option>
            <option value="java">Java</option>
            <option value="cpp">C++</option>
          </select>
        </div>
        
        <div className="control-group">
          <label>Documentation Type:</label>
          <select value={docType} onChange={(e) => setDocType(e.target.value)}>
            <option value="function">📋 Function Docs (Structured)</option>
            <option value="readme">📄 README (Role-Based)</option>
            <option value="explanation">💡 Explanation (Chain-of-Thought)</option>
            <option value="architecture">🏗️ Architecture (Few-Shot)</option>
          </select>
        </div>
      </div>

      <div className="editor-container">
        <div className="input-section">
          <h3>Your Code</h3>
          <textarea
            value={code}
            onChange={(e) => setCode(e.target.value)}
            placeholder="Paste your code here..."
            rows={20}
          />
        </div>

        <div className="output-section">
          <h3>Generated Documentation</h3>
          <div className="documentation">
            {loading ? (
              <div className="loading">Generating...</div>
            ) : documentation ? (
              <pre>{documentation}</pre>
            ) : (
              <p className="placeholder">Documentation will appear here</p>
            )}
          </div>
        </div>
      </div>

      <button onClick={generateDocs} disabled={!code || loading}>
        {loading ? 'Generating...' : '✨ Generate Documentation'}
      </button>
    </div>
  )
}

export default App