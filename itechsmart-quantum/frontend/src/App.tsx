import React, { useState, useEffect } from 'react';
import { 
  QuantumProvider, 
  useQuantum 
} from './contexts/QuantumContext';
import { Header } from './components/Header';
import { Dashboard } from './components/Dashboard';
import { QuantumCircuits } from './components/QuantumCircuits';
import { Optimization } from './components/Optimization';
import { Algorithms } from './components/Algorithms';
import { Jobs } from './components/Jobs';
import { Resources } from './components/Resources';
import './App.css';

type TabType = 'dashboard' | 'circuits' | 'optimization' | 'algorithms' | 'jobs' | 'resources';

function AppContent() {
  const [activeTab, setActiveTab] = useState<TabType>('dashboard');
  const { status, isLoading } = useQuantum();

  const tabs = [
    { id: 'dashboard' as TabType, label: 'Dashboard', icon: '📊' },
    { id: 'circuits' as TabType, label: 'Quantum Circuits', icon: '⚡' },
    { id: 'optimization' as TabType, label: 'Optimization', icon: '🎯' },
    { id: 'algorithms' as TabType, label: 'Algorithms', icon: '🧮' },
    { id: 'jobs' as TabType, label: 'Jobs', icon: '📋' },
    { id: 'resources' as TabType, label: 'Resources', icon: '💎' }
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Initializing Quantum Computing Service...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="flex">
        {/* Sidebar */}
        <div className="w-64 bg-white shadow-md min-h-screen">
          <nav className="p-4">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Quantum Computing</h2>
            <ul className="space-y-2">
              {tabs.map((tab) => (
                <li key={tab.id}>
                  <button
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
                      activeTab === tab.id
                        ? 'bg-blue-100 text-blue-700 font-medium'
                        : 'hover:bg-gray-100 text-gray-700'
                    }`}
                  >
                    <span className="mr-2">{tab.icon}</span>
                    {tab.label}
                  </button>
                </li>
              ))}
            </ul>
          </nav>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900">
              {tabs.find(t => t.id === activeTab)?.label}
            </h1>
            <p className="text-gray-600 mt-2">
              {status?.qiskit_available ? (
                <span className="flex items-center">
                  <span className="w-3 h-3 bg-green-500 rounded-full mr-2"></span>
                  Quantum computing capabilities available
                </span>
              ) : (
                <span className="flex items-center">
                  <span className="w-3 h-3 bg-yellow-500 rounded-full mr-2"></span>
                  Running in simulation mode
                </span>
              )}
            </p>
          </div>

          {/* Tab Content */}
          {activeTab === 'dashboard' && <Dashboard />}
          {activeTab === 'circuits' && <QuantumCircuits />}
          {activeTab === 'optimization' && <Optimization />}
          {activeTab === 'algorithms' && <Algorithms />}
          {activeTab === 'jobs' && <Jobs />}
          {activeTab === 'resources' && <Resources />}
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <QuantumProvider>
      <AppContent />
    </QuantumProvider>
  );
}

export default App;