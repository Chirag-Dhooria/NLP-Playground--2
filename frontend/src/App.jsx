import React, { useState } from 'react';
import TaskSelector from './components/TaskSelector';
import Dashboard from './components/Dashboard';

function App() {
  const [selectedTask, setSelectedTask] = useState(null);

  return (
    <div className="min-h-screen bg-gray-50 text-gray-800 font-sans">
      <nav className="bg-indigo-600 p-4 text-white shadow-lg">
        <h1 className="text-2xl font-bold">NLP Playground 2.0</h1>
      </nav>

      <main className="container mx-auto p-6">
        {!selectedTask ? (
          <TaskSelector onSelect={setSelectedTask} />
        ) : (
          <Dashboard task={selectedTask} onBack={() => setSelectedTask(null)} />
        )}
      </main>
    </div>
  );
}

export default App;