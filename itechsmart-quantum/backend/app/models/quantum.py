"""
iTechSmart Quantum Computing Models

Data models for quantum circuits, optimization problems, and results.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class QuantumAlgorithmType(Enum):
    """Types of quantum algorithms."""

    GROVER_SEARCH = "grover_search"
    SHOR_FACTORING = "shor_factoring"
    QAOA_OPTIMIZATION = "qaoa_optimization"
    VQE_EIGENVALUE = "vqe_eigenvalue"
    QUANTUM_ML = "quantum_ml"
    QUANTUM_ANNEALING = "quantum_annealing"
    QUANTUM_FOURIER = "quantum_fourier_transform"


class OptimizationType(Enum):
    """Types of optimization problems."""

    LINEAR_PROGRAMMING = "linear_programming"
    QUADRATIC_PROGRAMMING = "quadratic_programming"
    COMBINATORIAL_OPTIMIZATION = "combinatorial_optimization"
    CONSTRAINED_OPTIMIZATION = "constrained_optimization"
    UNCONSTRAINED_OPTIMIZATION = "unconstrained_optimization"


@dataclass
class QuantumCircuit:
    """Represents a quantum circuit."""

    id: str
    name: str
    circuit: Any  # Qiskit QuantumCircuit or None for classical
    n_qubits: int
    depth: int
    algorithm: str
    parameters: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    is_classical: bool = False
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "n_qubits": self.n_qubits,
            "depth": self.depth,
            "algorithm": self.algorithm,
            "parameters": self.parameters,
            "created_at": self.created_at.isoformat(),
            "is_classical": self.is_classical,
            "description": self.description,
        }


@dataclass
class OptimizationProblem:
    """Represents a quantum optimization problem."""

    id: str
    objective_function: str
    variables: List[str]
    constraints: List[Dict[str, Any]]
    quantum_program: Any = None  # Qiskit QuadraticProgram or None
    optimization_type: OptimizationType = OptimizationType.COMBINATORIAL_OPTIMIZATION
    created_at: datetime = field(default_factory=datetime.now)
    is_classical: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "objective_function": self.objective_function,
            "variables": self.variables,
            "constraints": self.constraints,
            "optimization_type": self.optimization_type.value,
            "created_at": self.created_at.isoformat(),
            "is_classical": self.is_classical,
            "metadata": self.metadata,
        }


@dataclass
class QuantumResult:
    """Represents the result of a quantum computation."""

    job_id: str
    algorithm: str
    backend: str
    status: str
    solution: Optional[List[float]] = None
    objective_value: Optional[float] = None
    measurement_counts: Optional[Dict[str, int]] = None
    probability: Optional[float] = None
    execution_time: Optional[float] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "job_id": self.job_id,
            "algorithm": self.algorithm,
            "backend": self.backend,
            "status": self.status,
            "solution": self.solution,
            "objective_value": self.objective_value,
            "measurement_counts": self.measurement_counts,
            "probability": self.probability,
            "execution_time": self.execution_time,
            "error": self.error,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }

    def is_successful(self) -> bool:
        """Check if the quantum computation was successful."""
        return self.status == "completed" and self.error is None


@dataclass
class QuantumJob:
    """Represents a quantum computing job."""

    job_id: str
    algorithm: QuantumAlgorithmType
    backend: str
    parameters: Dict[str, Any]
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    result: Optional[QuantumResult] = None
    priority: int = 0
    max_execution_time: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "job_id": self.job_id,
            "algorithm": self.algorithm.value,
            "backend": self.backend,
            "parameters": self.parameters,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "completed_at": (
                self.completed_at.isoformat() if self.completed_at else None
            ),
            "priority": self.priority,
            "max_execution_time": self.max_execution_time,
            "result": self.result.to_dict() if self.result else None,
        }

    def is_finished(self) -> bool:
        """Check if the job is finished."""
        return self.status in ["completed", "failed", "cancelled"]

    def is_running(self) -> bool:
        """Check if the job is currently running."""
        return self.status in ["queued", "running"]


@dataclass
class QuantumBackend:
    """Represents a quantum computing backend."""

    name: str
    type: str
    n_qubits: int
    connectivity: str  # 'all-to-all', 'linear', 'grid', etc.
    gate_fidelity: float
    readout_fidelity: float
    coherence_time: float  # in microseconds
    availability: bool
    queue_time: Optional[float] = None  # in seconds
    cost_per_execution: Optional[float] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "type": self.type,
            "n_qubits": self.n_qubits,
            "connectivity": self.connectivity,
            "gate_fidelity": self.gate_fidelity,
            "readout_fidelity": self.readout_fidelity,
            "coherence_time": self.coherence_time,
            "availability": self.availability,
            "queue_time": self.queue_time,
            "cost_per_execution": self.cost_per_execution,
            "description": self.description,
        }

    def is_available(self) -> bool:
        """Check if backend is available for use."""
        return self.availability and (self.queue_time is not None)


@dataclass
class QuantumBenchmark:
    """Represents quantum algorithm benchmark results."""

    algorithm: str
    backend: str
    problem_size: int
    execution_time: float
    success_rate: float
    accuracy: float
    resource_usage: Dict[str, Any]
    benchmark_date: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "algorithm": self.algorithm,
            "backend": self.backend,
            "problem_size": self.problem_size,
            "execution_time": self.execution_time,
            "success_rate": self.success_rate,
            "accuracy": self.accuracy,
            "resource_usage": self.resource_usage,
            "benchmark_date": self.benchmark_date.isoformat(),
        }


@dataclass
class QuantumResource:
    """Represents quantum computing resources."""

    name: str
    type: str
    capacity: int
    current_usage: int
    availability: float  # percentage
    cost_per_hour: Optional[float] = None
    specifications: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "type": self.type,
            "capacity": self.capacity,
            "current_usage": self.current_usage,
            "availability": self.availability,
            "cost_per_hour": self.cost_per_hour,
            "specifications": self.specifications,
        }

    def utilization_rate(self) -> float:
        """Calculate current utilization rate."""
        if self.capacity == 0:
            return 0.0
        return (self.current_usage / self.capacity) * 100

    def is_available(self, required_capacity: int = 1) -> bool:
        """Check if resource is available for required capacity."""
        return (self.capacity - self.current_usage) >= required_capacity


@dataclass
class QuantumApplication:
    """Represents a quantum application use case."""

    name: str
    description: str
    domain: str  # 'finance', 'healthcare', 'logistics', etc.
    algorithm: QuantumAlgorithmType
    expected_speedup: float
    complexity: str  # 'low', 'medium', 'high'
    requirements: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "description": self.description,
            "domain": self.domain,
            "algorithm": self.algorithm.value,
            "expected_speedup": self.expected_speedup,
            "complexity": self.complexity,
            "requirements": self.requirements,
            "created_at": self.created_at.isoformat(),
        }


# Quantum-specific error types
class QuantumError(Exception):
    """Base class for quantum computing errors."""

    pass


class QuantumCircuitError(QuantumError):
    """Error in quantum circuit creation or execution."""

    pass


class QuantumBackendError(QuantumError):
    """Error related to quantum backend operations."""

    pass


class QuantumOptimizationError(QuantumError):
    """Error in quantum optimization."""

    pass


class QuantumResourceError(QuantumError):
    """Error related to quantum resource allocation."""

    pass
