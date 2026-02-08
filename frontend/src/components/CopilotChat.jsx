import React, { useState } from 'react';
import axios from 'axios';
import { Send, Bot } from 'lucide-react';

const CopilotChat = ({ filename }) => {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([
    { role: 'bot', text: "Hello! I'm your Dataset Consultant. Ask me about missing values or model advice." }
  ]);

  const handleSend = async () => {
    if (!query) return;
    const userMsg = { role: 'user', text: query };
    setMessages(prev => [...prev, userMsg]);
    setQuery("");

    try {
      const res = await axios.post('http://localhost:8000/copilot/consult', {
        filename,
        user_query: userMsg.text
      });
      setMessages(prev => [...prev, { role: 'bot', text: res.data.response }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', text: "Error connecting to AI." }]);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="bg-indigo-50 p-2 border-b flex items-center gap-2">
        <Bot size={20} className="text-indigo-600"/>
        <span className="font-bold text-indigo-900">AI Copilot</span>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`p-2 rounded-lg max-w-[80%] text-sm ${m.role === 'user' ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
              {m.text}
            </div>
          </div>
        ))}
      </div>

      <div className="p-2 border-t flex gap-2">
        <input 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask about your data..."
          className="flex-1 p-2 border rounded focus:outline-none focus:border-indigo-500"
        />
        <button onClick={handleSend} className="p-2 bg-indigo-600 text-white rounded hover:bg-indigo-700">
          <Send size={18} />
        </button>
      </div>
    </div>
  );
};

export default CopilotChat;