import React from 'react';
import { MessageSquare, FileText, HelpCircle, BarChart2, Bot } from 'lucide-react';

const TaskCard = ({ title, icon: Icon, onClick }) => (
  <div 
    onClick={onClick}
    className="bg-white p-6 rounded-xl shadow-md hover:shadow-xl transition-all cursor-pointer border-2 border-transparent hover:border-indigo-500 flex flex-col items-center gap-4"
  >
    <div className="p-4 bg-indigo-100 rounded-full text-indigo-600">
      <Icon size={32} />
    </div>
    <h3 className="text-xl font-semibold">{title}</h3>
  </div>
);

const TaskSelector = ({ onSelect }) => {
  return (
    <div className="flex flex-col items-center justify-center h-[80vh]">
      <h2 className="text-3xl font-bold mb-8">Select your NLP Mission</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl w-full">
        <TaskCard title="Text Classification" icon={BarChart2} onClick={() => onSelect('classification')} />
        <TaskCard title="Summarization" icon={FileText} onClick={() => onSelect('summarization')} />
        <TaskCard title="Question Answering" icon={HelpCircle} onClick={() => onSelect('qa')} />
        <TaskCard title="Sentiment Analysis" icon={MessageSquare} onClick={() => onSelect('sentiment')} />
        <TaskCard title="Ask Your Document (RAG)" icon={Bot} onClick={() => onSelect('rag')} />
      </div>
    </div>
  );
};

export default TaskSelector;
