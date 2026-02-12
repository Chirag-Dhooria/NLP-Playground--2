import React, { useState } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';
import 'chart.js/auto';
import CopilotChat from './CopilotChat';
import DocumentChat from './DocumentChat';

const API_URL = 'http://localhost:8000';

const Dashboard = ({ task, onBack }) => {
  const [file, setFile] = useState(null);
  const [metadata, setMetadata] = useState(null);
  const [config, setConfig] = useState({});
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async (e) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) {
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const res = await axios.post(`${API_URL}/upload`, formData);
      setFile(res.data.filename);
      setMetadata(res.data.metadata);
      setConfig({});
      setResults(null);
    } catch (err) {
      console.error('Upload failed', err);
      alert(err.response?.data?.detail || 'Failed to upload dataset.');
    }
  };

  const runExperiment = async () => {
    setLoading(true);
    try {
      const payload = {
        task_type: task,
        filename: file,
        input_column: config.input_col,
        target_column: config.target_col,
        context_column: config.context_col,
        hyperparameters: { C: 1.0 },
      };

      const res = await axios.post(`${API_URL}/train`, payload);
      setResults(res.data);
    } catch (err) {
      alert(`Error running experiment: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  if (task === 'rag') {
    return (
      <div className="h-[85vh] bg-white p-6 rounded-lg shadow flex flex-col">
        <button onClick={onBack} className="text-sm text-gray-500 mb-4 hover:underline w-fit">← Back to Tasks</button>
        <h2 className="text-2xl font-bold mb-4">Ask Your Document Workspace</h2>
        <div className="flex-1 rounded-lg shadow border-2 border-emerald-100 overflow-hidden">
          <DocumentChat />
        </div>
      </div>
    );
  }

  const requiresTarget = task === 'classification';
  const requiresContext = task === 'qa';
  const canRun =
    !!file &&
    !!config.input_col &&
    (!requiresTarget || !!config.target_col) &&
    (!requiresContext || !!config.context_col) &&
    !loading;

  return (
    <div className="flex gap-6 h-[85vh]">
      <div className="w-1/3 bg-white p-6 rounded-lg shadow overflow-y-auto">
        <button onClick={onBack} className="text-sm text-gray-500 mb-4 hover:underline">← Back to Tasks</button>
        <h2 className="text-2xl font-bold capitalize mb-4">{task} Workspace</h2>

        <div className="mb-6">
          <label className="block text-sm font-medium mb-2">1. Upload Data (CSV)</label>
          <input type="file" accept=".csv" onChange={handleUpload} className="w-full p-2 border rounded" />
        </div>

        {metadata && (
          <div className="mb-6 space-y-4">
            <label className="block text-sm font-medium">2. Select Input Column</label>
            <select
              className="w-full p-2 border rounded"
              value={config.input_col || ''}
              onChange={(e) => setConfig({ ...config, input_col: e.target.value })}
            >
              <option value="">Select Column...</option>
              {metadata.column_names.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>

            {requiresTarget && (
              <>
                <label className="block text-sm font-medium">Target Column</label>
                <select
                  className="w-full p-2 border rounded"
                  value={config.target_col || ''}
                  onChange={(e) => setConfig({ ...config, target_col: e.target.value })}
                >
                  <option value="">Select Target...</option>
                  {metadata.column_names.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </>
            )}

            {requiresContext && (
              <>
                <label className="block text-sm font-medium">Context Column</label>
                <select
                  className="w-full p-2 border rounded"
                  value={config.context_col || ''}
                  onChange={(e) => setConfig({ ...config, context_col: e.target.value })}
                >
                  <option value="">Select Context...</option>
                  {metadata.column_names.map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </>
            )}
          </div>
        )}

        <button
          onClick={runExperiment}
          disabled={!canRun}
          className="w-full bg-indigo-600 text-white py-3 rounded-lg font-bold hover:bg-indigo-700 disabled:bg-gray-400"
        >
          {loading ? 'Training...' : 'Run Experiment'}
        </button>
      </div>

      <div className="w-2/3 flex flex-col gap-6">
        <div className="flex-1 bg-white p-6 rounded-lg shadow overflow-auto">
          <h3 className="text-xl font-bold mb-4">Results Dashboard</h3>
          {results ? (
            <div>
              {results.type === 'classification_metrics' && (
                <pre className="bg-gray-100 p-4 rounded text-xs">{JSON.stringify(results.metrics, null, 2)}</pre>
              )}
              {results.type === 'sentiment_analysis' && (
                <div className="h-64 w-full">
                  <Bar
                    data={{
                      labels: Object.keys(results.results),
                      datasets: [
                        {
                          label: 'Sentiment Distribution',
                          data: Object.values(results.results),
                          backgroundColor: ['#4ade80', '#f87171', '#94a3b8'],
                        },
                      ],
                    }}
                  />
                </div>
              )}
              {results.type === 'text_output' && results.summaries && (
                <div className="space-y-3">
                  {results.summaries.map((item, index) => (
                    <div key={index} className="bg-gray-100 p-3 rounded text-sm">
                      <p className="font-semibold">Summary {index + 1}</p>
                      <p>{item.summary_text}</p>
                    </div>
                  ))}
                </div>
              )}
              {results.type === 'text_output' && results.qa_results && (
                <div className="space-y-3">
                  {results.qa_results.map((item, index) => (
                    <div key={index} className="bg-gray-100 p-3 rounded text-sm">
                      <p className="font-semibold">Q: {item.question}</p>
                      <p>A: {item.answer}</p>
                      <p className="text-xs text-gray-500">Score: {Number(item.score).toFixed(4)}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="text-gray-400 flex items-center justify-center h-full">Run an experiment to see results</div>
          )}
        </div>

        <div className="h-1/3 flex gap-6">
          <div className="w-1/2 bg-white rounded-lg shadow border-2 border-indigo-100 overflow-hidden">
            {file && <CopilotChat filename={file} />}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
