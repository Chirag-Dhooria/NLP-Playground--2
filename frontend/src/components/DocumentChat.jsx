import React, { useState } from 'react';
import axios from 'axios';
import { FileText, Send, Bot } from 'lucide-react';

const DocumentChat = () => {
  const [documentName, setDocumentName] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleUpload = async (event) => {
    const selectedFile = event.target.files[0];
    if (!selectedFile) return;
    const formData = new FormData();
    formData.append("file", selectedFile);
    setLoading(true);
    setAnswer("");
    setSources([]);

    try {
      const res = await axios.post("http://localhost:8000/rag/upload", formData);
      setDocumentName(res.data.filename);
      setAnswer(`Indexed ${res.data.chunks_indexed} chunks across ${res.data.pages_indexed} pages.`);
    } catch (error) {
      setAnswer("Failed to upload and index the document.");
    } finally {
      setLoading(false);
    }
  };

  const handleAsk = async () => {
    if (!question || !documentName) return;
    setLoading(true);
    setAnswer("");
    setSources([]);
    try {
      const res = await axios.post("http://localhost:8000/rag/query", {
        filename: documentName,
        question,
      });
      setAnswer(res.data.answer);
      setSources(res.data.sources || []);
    } catch (error) {
      setAnswer("Failed to query the document.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="bg-emerald-50 p-2 border-b flex items-center gap-2">
        <Bot size={20} className="text-emerald-600" />
        <span className="font-bold text-emerald-900">Ask Your Document</span>
      </div>

      <div className="p-3 border-b text-sm text-gray-600 flex items-center gap-2">
        <FileText size={16} />
        <span>{documentName || "Upload a PDF to begin"}</span>
      </div>

      <div className="p-3 border-b">
        <input type="file" accept="application/pdf" onChange={handleUpload} />
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3 text-sm">
        {loading && <div className="text-gray-500">Working on your request...</div>}
        {answer && (
          <div className="bg-gray-100 p-3 rounded">
            <p className="whitespace-pre-line">{answer}</p>
          </div>
        )}
        {sources.length > 0 && (
          <div className="space-y-2">
            <p className="font-semibold text-gray-700">Citations</p>
            <ul className="space-y-1 text-xs text-gray-600">
              {sources.map((source, index) => (
                <li key={`${source.page}-${source.chunk}-${index}`}>
                  Page {source.page}, Chunk {source.chunk}: {source.snippet}...
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <div className="p-2 border-t flex gap-2">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleAsk()}
          placeholder="Ask about the document..."
          className="flex-1 p-2 border rounded focus:outline-none focus:border-emerald-500"
        />
        <button
          onClick={handleAsk}
          disabled={!documentName || loading}
          className="p-2 bg-emerald-600 text-white rounded hover:bg-emerald-700 disabled:bg-gray-400"
        >
          <Send size={18} />
        </button>
      </div>
    </div>
  );
};

export default DocumentChat;
