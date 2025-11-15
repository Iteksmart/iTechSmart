import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import { Play, Save, Download, Upload } from 'lucide-react';
import { sandboxApi } from '../services/api';
import type { Sandbox, Process } from '../types';
import { parseErrorMessage, getLanguageFromExtension } from '../utils/helpers';

const CodeEditor: React.FC = () => {
  const [searchParams] = useSearchParams();
  const sandboxId = searchParams.get('sandbox');
  
  const [sandbox, setSandbox] = useState<Sandbox | null>(null);
  const [code, setCode] = useState('# Write your code here\nprint("Hello, World!")');
  const [language, setLanguage] = useState('python');
  const [output, setOutput] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (sandboxId) {
      loadSandbox();
    }
  }, [sandboxId]);

  const loadSandbox = async () => {
    if (!sandboxId) return;
    
    try {
      const data = await sandboxApi.get(sandboxId);
      setSandbox(data);
    } catch (err) {
      setError(parseErrorMessage(err));
    }
  };

  const handleRun = async () => {
    if (!sandboxId) {
      alert('Please select a sandbox first');
      return;
    }

    try {
      setIsRunning(true);
      setOutput('Running...\n');
      setError(null);

      const process = await sandboxApi.executeCode(sandboxId, {
        code,
        language,
        timeout: 30,
      });

      // Poll for completion
      let completed = false;
      let attempts = 0;
      const maxAttempts = 60; // 30 seconds max

      while (!completed && attempts < maxAttempts) {
        await new Promise((resolve) => setTimeout(resolve, 500));
        
        // In a real implementation, we'd poll the process status
        // For now, we'll just show the initial output
        completed = true;
      }

      if (process.stdout) {
        setOutput(process.stdout);
      }
      if (process.stderr) {
        setOutput((prev) => prev + '\n' + process.stderr);
      }
      if (process.exit_code !== 0) {
        setError(`Process exited with code ${process.exit_code}`);
      }
    } catch (err) {
      setError(parseErrorMessage(err));
      setOutput('');
    } finally {
      setIsRunning(false);
    }
  };

  const handleSave = () => {
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `code.${language === 'python' ? 'py' : language === 'javascript' ? 'js' : 'txt'}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleUpload = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (e) => {
          const content = e.target?.result as string;
          setCode(content);
          
          // Detect language from file extension
          const ext = file.name.split('.').pop() || '';
          const detectedLang = getLanguageFromExtension(ext);
          setLanguage(detectedLang);
        };
        reader.readAsText(file);
      }
    };
    input.click();
  };

  const languages = [
    { value: 'python', label: 'Python' },
    { value: 'javascript', label: 'JavaScript' },
    { value: 'typescript', label: 'TypeScript' },
    { value: 'java', label: 'Java' },
    { value: 'cpp', label: 'C++' },
    { value: 'go', label: 'Go' },
    { value: 'rust', label: 'Rust' },
  ];

  return (
    <div>
      {/* Header */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: 'var(--spacing-lg)',
        }}
      >
        <div>
          <h1 style={{ margin: 0, fontSize: '32px', fontWeight: 'bold' }}>
            Code Editor
          </h1>
          {sandbox && (
            <p
              style={{
                margin: '8px 0 0 0',
                fontSize: '16px',
                color: 'var(--text-secondary)',
              }}
            >
              Sandbox: {sandbox.name}
            </p>
          )}
        </div>

        <div style={{ display: 'flex', gap: 'var(--spacing-sm)' }}>
          <select
            className="form-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
          >
            {languages.map((lang) => (
              <option key={lang.value} value={lang.value}>
                {lang.label}
              </option>
            ))}
          </select>
          <button className="btn btn-secondary" onClick={handleUpload}>
            <Upload size={16} />
            Upload
          </button>
          <button className="btn btn-secondary" onClick={handleSave}>
            <Save size={16} />
            Save
          </button>
          <button
            className="btn btn-primary"
            onClick={handleRun}
            disabled={isRunning || !sandboxId}
          >
            {isRunning ? (
              <>
                <div className="spinner" />
                Running...
              </>
            ) : (
              <>
                <Play size={16} />
                Run Code
              </>
            )}
          </button>
        </div>
      </div>

      {/* Editor and Output */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-lg)', height: 'calc(100vh - 250px)' }}>
        {/* Code Editor */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <div
            style={{
              padding: 'var(--spacing-md)',
              borderBottom: '1px solid var(--border-color)',
              background: 'var(--bg-tertiary)',
            }}
          >
            <h3 style={{ margin: 0, fontSize: '14px', fontWeight: 600 }}>
              Code
            </h3>
          </div>
          <Editor
            height="100%"
            language={language}
            value={code}
            onChange={(value) => setCode(value || '')}
            theme="vs-light"
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              lineNumbers: 'on',
              scrollBeyondLastLine: false,
              automaticLayout: true,
            }}
          />
        </div>

        {/* Output */}
        <div className="card" style={{ padding: 0, overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <div
            style={{
              padding: 'var(--spacing-md)',
              borderBottom: '1px solid var(--border-color)',
              background: 'var(--bg-tertiary)',
            }}
          >
            <h3 style={{ margin: 0, fontSize: '14px', fontWeight: 600 }}>
              Output
            </h3>
          </div>
          <div
            style={{
              flex: 1,
              padding: 'var(--spacing-md)',
              fontFamily: 'var(--font-mono)',
              fontSize: '14px',
              overflowY: 'auto',
              background: '#1e1e1e',
              color: '#d4d4d4',
            }}
          >
            {error && (
              <div style={{ color: '#f48771', marginBottom: '8px' }}>
                Error: {error}
              </div>
            )}
            <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
              {output || 'Output will appear here...'}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CodeEditor;