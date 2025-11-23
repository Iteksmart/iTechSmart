import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';

// Types
interface QuantumStatus {
  qiskit_available: boolean;
  available_backends: number;
  active_jobs: number;
  total_jobs: number;
  service_status: string;
}

interface QuantumJob {
  job_id: string;
  algorithm: string;
  backend: string;
  status: string;
  created_at: string;
  completed_at?: string;
  solution?: number[];
  objective_value?: number;
  execution_time?: number;
  error?: string;
}

interface QuantumCircuit {
  id: string;
  name: string;
  n_qubits: number;
  depth: number;
  algorithm: string;
  created_at: string;
  parameters: Record<string, any>;
}

interface OptimizationProblem {
  id: string;
  objective_function: string;
  variables: string[];
  constraints: Record<string, any>[];
  optimization_type: string;
  created_at: string;
}

interface QuantumState {
  status: QuantumStatus | null;
  jobs: QuantumJob[];
  circuits: QuantumCircuit[];
  optimization_problems: OptimizationProblem[];
  isLoading: boolean;
  error: string | null;
}

type QuantumAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_STATUS'; payload: QuantumStatus }
  | { type: 'SET_JOBS'; payload: QuantumJob[] }
  | { type: 'ADD_JOB'; payload: QuantumJob }
  | { type: 'UPDATE_JOB'; payload: QuantumJob }
  | { type: 'SET_CIRCUITS'; payload: QuantumCircuit[] }
  | { type: 'ADD_CIRCUIT'; payload: QuantumCircuit }
  | { type: 'SET_OPTIMIZATION_PROBLEMS'; payload: OptimizationProblem[] }
  | { type: 'ADD_OPTIMIZATION_PROBLEM'; payload: OptimizationProblem };

// Initial state
const initialState: QuantumState = {
  status: null,
  jobs: [],
  circuits: [],
  optimization_problems: [],
  isLoading: false,
  error: null,
};

// Reducer
function quantumReducer(state: QuantumState, action: QuantumAction): QuantumState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    
    case 'SET_ERROR':
      return { ...state, error: action.payload, isLoading: false };
    
    case 'SET_STATUS':
      return { ...state, status: action.payload };
    
    case 'SET_JOBS':
      return { ...state, jobs: action.payload };
    
    case 'ADD_JOB':
      return { ...state, jobs: [action.payload, ...state.jobs] };
    
    case 'UPDATE_JOB':
      return {
        ...state,
        jobs: state.jobs.map(job =>
          job.job_id === action.payload.job_id ? action.payload : job
        )
      };
    
    case 'SET_CIRCUITS':
      return { ...state, circuits: action.payload };
    
    case 'ADD_CIRCUIT':
      return { ...state, circuits: [action.payload, ...state.circuits] };
    
    case 'SET_OPTIMIZATION_PROBLEMS':
      return { ...state, optimization_problems: action.payload };
    
    case 'ADD_OPTIMIZATION_PROBLEM':
      return { ...state, optimization_problems: [action.payload, ...state.optimization_problems] };
    
    default:
      return state;
  }
}

// Context
interface QuantumContextType {
  state: QuantumState;
  dispatch: React.Dispatch<QuantumAction>;
  // API functions
  fetchStatus: () => Promise<void>;
  fetchJobs: () => Promise<void>;
  createGroverCircuit: (searchSpaceSize: number, targetStates: number[]) => Promise<QuantumCircuit>;
  executeCircuit: (circuitId: string, backend?: string, shots?: number) => Promise<QuantumJob>;
  createOptimizationProblem: (objectiveFunction: string, variables: string[], constraints: Record<string, any>[]) => Promise<OptimizationProblem>;
  solveOptimization: (problemId: string, backend?: string) => Promise<QuantumJob>;
  runDemo: (type: 'grover' | 'optimization') => Promise<any>;
  cancelJob: (jobId: string) => Promise<void>;
}

const QuantumContext = createContext<QuantumContextType | undefined>(undefined);

// API base URL
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8042/api/v1/quantum';

// Provider
interface QuantumProviderProps {
  children: ReactNode;
}

export function QuantumProvider({ children }: QuantumProviderProps) {
  const [state, dispatch] = useReducer(quantumReducer, initialState);

  // API helper
  async function apiCall(endpoint: string, options: RequestInit = {}) {
    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API call failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Fetch quantum status
  async function fetchStatus() {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const data = await apiCall('/status');
      dispatch({ type: 'SET_STATUS', payload: data });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: 'Failed to fetch quantum status' });
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }

  // Fetch jobs
  async function fetchJobs() {
    try {
      const data = await apiCall('/jobs');
      dispatch({ type: 'SET_JOBS', payload: data.jobs || [] });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: 'Failed to fetch jobs' });
    }
  }

  // Create Grover circuit
  async function createGroverCircuit(searchSpaceSize: number, targetStates: number[]): Promise<QuantumCircuit> {
    try {
      const data = await apiCall('/circuit/grover', {
        method: 'POST',
        body: JSON.stringify({
          search_space_size: searchSpaceSize,
          target_states: targetStates,
        }),
      });

      dispatch({ type: 'ADD_CIRCUIT', payload: data.circuit });
      return data.circuit;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: 'Failed to create Grover circuit' });
      throw error;
    }
  }

  // Execute circuit
  async function executeCircuit(circuitId: string, backend = 'simulator', shots = 1024): Promise<QuantumJob> {
    try {
      const data = await apiCall('/circuit/execute', {
        method: 'POST',
        body: JSON.stringify({ circuit_id: circuitId, backend, shots }),
      });

      dispatch({ type: 'ADD_JOB', payload: data.result });
      return data.result;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: 'Failed to execute circuit' });
      throw error;
    }
  }

  // Create optimization problem
  async function createOptimizationProblem(
    objectiveFunction: string,
    variables: string[],
    constraints: Record<string, any>[]
  ): Promise<OptimizationProblem> {
    try {
      const data = await apiCall('/optimization', {
        method: 'POST',
        body: JSON.stringify({
          objective_function: objectiveFunction,
          variables,
          constraints,
        }),
      });

      dispatch({ type: 'ADD_OPTIMIZATION_PROBLEM', payload: data.problem });
      return data.problem;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: 'Failed to create optimization problem' });
      throw error;
    }
  }

  // Solve optimization
  async function solveOptimization(problemId: string, backend = 'simulator'): Promise<QuantumJob> {
    try {
      const data = await apiCall('/optimization/solve', {
        method: 'POST',
        body: JSON.stringify({ problem_id: problemId, backend }),
      });

      dispatch({ type: 'ADD_JOB', payload: data.result });
      return data.result;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: 'Failed to solve optimization' });
      throw error;
    }
  }

  // Run demo
  async function runDemo(type: 'grover' | 'optimization') {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const data = await apiCall(`/demo/${type}`, { method: 'POST' });
      return data;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: `Failed to run ${type} demo` });
      throw error;
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  }

  // Cancel job
  async function cancelJob(jobId: string) {
    try {
      await apiCall(`/jobs/${jobId}`, { method: 'DELETE' });
      
      // Update job status
      const updatedJob = { ...state.jobs.find(j => j.job_id === jobId)!, status: 'cancelled' as const };
      dispatch({ type: 'UPDATE_JOB', payload: updatedJob });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: 'Failed to cancel job' });
      throw error;
    }
  }

  // Initialize on mount
  useEffect(() => {
    fetchStatus();
    fetchJobs();
  }, []);

  const value: QuantumContextType = {
    state,
    dispatch,
    fetchStatus,
    fetchJobs,
    createGroverCircuit,
    executeCircuit,
    createOptimizationProblem,
    solveOptimization,
    runDemo,
    cancelJob,
  };

  return (
    <QuantumContext.Provider value={value}>
      {children}
    </QuantumContext.Provider>
  );
}

// Hook
export function useQuantum() {
  const context = useContext(QuantumContext);
  if (context === undefined) {
    throw new Error('useQuantum must be used within a QuantumProvider');
  }
  return context;
}