"""
iTechSmart Quantum Computing Configuration

Configuration settings for quantum computing services and backends.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import os
from enum import Enum


class QuantumBackendType(Enum):
    """Types of quantum computing backends."""

    IBM_QUANTUM = "ibm_quantum"
    D_WAVE = "d_wave"
    GOOGLE_QUANTUM = "google_quantum"
    AMAZON_BRAKET = "amazon_braket"
    MICROSOFT_QUANTUM = "microsoft_quantum"
    SIMULATOR = "simulator"
    HYBRID = "hybrid"


@dataclass
class QuantumBackendConfig:
    """Configuration for a quantum backend."""

    name: str
    backend_type: QuantumBackendType
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    n_qubits: int = 0
    connectivity: str = "all-to-all"
    gate_fidelity: float = 0.99
    readout_fidelity: float = 0.95
    coherence_time: float = 100.0  # microseconds
    max_shots: int = 10000
    timeout: int = 300  # seconds
    priority: int = 0
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "backend_type": self.backend_type.value,
            "endpoint": self.endpoint,
            "n_qubits": self.n_qubits,
            "connectivity": self.connectivity,
            "gate_fidelity": self.gate_fidelity,
            "readout_fidelity": self.readout_fidelity,
            "coherence_time": self.coherence_time,
            "max_shots": self.max_shots,
            "timeout": self.timeout,
            "priority": self.priority,
            "enabled": self.enabled,
        }


@dataclass
class QuantumAlgorithmConfig:
    """Configuration for quantum algorithms."""

    name: str
    algorithm_type: str
    default_iterations: int = 100
    convergence_threshold: float = 1e-6
    max_execution_time: float = 300.0  # seconds
    required_qubits: int = 2
    supported_backends: List[QuantumBackendType] = None

    def __post_init__(self):
        if self.supported_backends is None:
            self.supported_backends = [QuantumBackendType.SIMULATOR]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "algorithm_type": self.algorithm_type,
            "default_iterations": self.default_iterations,
            "convergence_threshold": self.convergence_threshold,
            "max_execution_time": self.max_execution_time,
            "required_qubits": self.required_qubits,
            "supported_backends": [b.value for b in self.supported_backends],
        }


@dataclass
class QuantumConfig:
    """Main quantum computing configuration."""

    # Service settings
    service_name: str = "iTechSmart Quantum Computing"
    version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # Backend configurations
    backends: Dict[str, QuantumBackendConfig] = None

    # Algorithm configurations
    algorithms: Dict[str, QuantumAlgorithmConfig] = None

    # Resource limits
    max_concurrent_jobs: int = 10
    max_job_queue_size: int = 100
    default_timeout: int = 300  # seconds
    max_result_size: int = 100 * 1024 * 1024  # 100MB

    # Performance settings
    cache_results: bool = True
    cache_ttl: int = 3600  # seconds
    enable_monitoring: bool = True
    enable_benchmarks: bool = True

    # Security settings
    require_authentication: bool = True
    allowed_algorithms: List[str] = None
    rate_limiting: bool = True
    rate_limit_per_minute: int = 60

    def __post_init__(self):
        if self.backends is None:
            self.backends = self._get_default_backends()
        if self.algorithms is None:
            self.algorithms = self._get_default_algorithms()
        if self.allowed_algorithms is None:
            self.allowed_algorithms = [alg for alg in self.algorithms.keys()]

    def _get_default_backends(self) -> Dict[str, QuantumBackendConfig]:
        """Get default backend configurations."""
        return {
            "simulator": QuantumBackendConfig(
                name="simulator",
                backend_type=QuantumBackendType.SIMULATOR,
                n_qubits=32,
                connectivity="all-to-all",
                gate_fidelity=1.0,
                readout_fidelity=1.0,
                coherence_time=float("inf"),
                max_shots=100000,
                timeout=60,
                priority=10,
                enabled=True,
            ),
            "ibm_quantum": QuantumBackendConfig(
                name="ibm_quantum",
                backend_type=QuantumBackendType.IBM_QUANTUM,
                endpoint=os.getenv("IBM_QUANTUM_ENDPOINT"),
                api_key=os.getenv("IBM_QUANTUM_API_KEY"),
                n_qubits=27,
                connectivity="heavy_hex",
                gate_fidelity=0.99,
                readout_fidelity=0.95,
                coherence_time=100.0,
                max_shots=10000,
                timeout=300,
                priority=5,
                enabled=bool(os.getenv("IBM_QUANTUM_API_KEY")),
            ),
            "hybrid": QuantumBackendConfig(
                name="hybrid",
                backend_type=QuantumBackendType.HYBRID,
                n_qubits=64,
                connectivity="hybrid",
                gate_fidelity=0.98,
                readout_fidelity=0.93,
                coherence_time=200.0,
                max_shots=50000,
                timeout=180,
                priority=7,
                enabled=True,
            ),
        }

    def _get_default_algorithms(self) -> Dict[str, QuantumAlgorithmConfig]:
        """Get default algorithm configurations."""
        return {
            "grover_search": QuantumAlgorithmConfig(
                name="Grover's Search",
                algorithm_type="search",
                default_iterations=10,
                convergence_threshold=1e-6,
                max_execution_time=120.0,
                required_qubits=2,
                supported_backends=[
                    QuantumBackendType.SIMULATOR,
                    QuantumBackendType.IBM_QUANTUM,
                    QuantumBackendType.HYBRID,
                ],
            ),
            "qaoa_optimization": QuantumAlgorithmConfig(
                name="QAOA Optimization",
                algorithm_type="optimization",
                default_iterations=100,
                convergence_threshold=1e-6,
                max_execution_time=300.0,
                required_qubits=4,
                supported_backends=[
                    QuantumBackendType.SIMULATOR,
                    QuantumBackendType.IBM_QUANTUM,
                    QuantumBackendType.HYBRID,
                ],
            ),
            "vqe_eigenvalue": QuantumAlgorithmConfig(
                name="VQE Eigenvalue",
                algorithm_type="eigenvalue",
                default_iterations=200,
                convergence_threshold=1e-6,
                max_execution_time=300.0,
                required_qubits=2,
                supported_backends=[
                    QuantumBackendType.SIMULATOR,
                    QuantumBackendType.IBM_QUANTUM,
                    QuantumBackendType.HYBRID,
                ],
            ),
            "quantum_monte_carlo": QuantumAlgorithmConfig(
                name="Quantum Monte Carlo",
                algorithm_type="simulation",
                default_iterations=500,
                convergence_threshold=1e-4,
                max_execution_time=600.0,
                required_qubits=8,
                supported_backends=[
                    QuantumBackendType.SIMULATOR,
                    QuantumBackendType.HYBRID,
                ],
            ),
            "quantum_machine_learning": QuantumAlgorithmConfig(
                name="Quantum Machine Learning",
                algorithm_type="ml",
                default_iterations=1000,
                convergence_threshold=1e-4,
                max_execution_time=600.0,
                required_qubits=4,
                supported_backends=[
                    QuantumBackendType.SIMULATOR,
                    QuantumBackendType.HYBRID,
                ],
            ),
        }

    def get_backend(self, name: str) -> Optional[QuantumBackendConfig]:
        """Get backend configuration by name."""
        return self.backends.get(name)

    def get_algorithm(self, name: str) -> Optional[QuantumAlgorithmConfig]:
        """Get algorithm configuration by name."""
        return self.algorithms.get(name)

    def get_enabled_backends(self) -> Dict[str, QuantumBackendConfig]:
        """Get all enabled backend configurations."""
        return {
            name: config for name, config in self.backends.items() if config.enabled
        }

    def get_available_algorithms(self, backend_name: str) -> List[str]:
        """Get algorithms available for a specific backend."""
        backend = self.get_backend(backend_name)
        if not backend:
            return []

        available = []
        for alg_name, alg_config in self.algorithms.items():
            if backend.backend_type in alg_config.supported_backends:
                available.append(alg_name)
        return available

    def is_algorithm_allowed(self, algorithm_name: str) -> bool:
        """Check if algorithm is allowed."""
        return algorithm_name in self.allowed_algorithms

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "service_name": self.service_name,
            "version": self.version,
            "debug": self.debug,
            "log_level": self.log_level,
            "backends": {
                name: config.to_dict() for name, config in self.backends.items()
            },
            "algorithms": {
                name: config.to_dict() for name, config in self.algorithms.items()
            },
            "max_concurrent_jobs": self.max_concurrent_jobs,
            "max_job_queue_size": self.max_job_queue_size,
            "default_timeout": self.default_timeout,
            "max_result_size": self.max_result_size,
            "cache_results": self.cache_results,
            "cache_ttl": self.cache_ttl,
            "enable_monitoring": self.enable_monitoring,
            "enable_benchmarks": self.enable_benchmarks,
            "require_authentication": self.require_authentication,
            "allowed_algorithms": self.allowed_algorithms,
            "rate_limiting": self.rate_limiting,
            "rate_limit_per_minute": self.rate_limit_per_minute,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QuantumConfig":
        """Create configuration from dictionary."""
        # Recreate backend configurations
        backends = {}
        if data.get("backends"):
            for name, backend_data in data["backends"].items():
                backend_data["backend_type"] = QuantumBackendType(
                    backend_data["backend_type"]
                )
                backends[name] = QuantumBackendConfig(**backend_data)

        # Recreate algorithm configurations
        algorithms = {}
        if data.get("algorithms"):
            for name, alg_data in data["algorithms"].items():
                supported_backends = []
                for backend_type in alg_data.get("supported_backends", []):
                    supported_backends.append(QuantumBackendType(backend_type))
                alg_data["supported_backends"] = supported_backends
                algorithms[name] = QuantumAlgorithmConfig(**alg_data)

        # Remove complex objects for main config creation
        main_data = {
            k: v for k, v in data.items() if k not in ["backends", "algorithms"]
        }
        main_data["backends"] = backends
        main_data["algorithms"] = algorithms

        return cls(**main_data)

    @classmethod
    def from_env(cls) -> "QuantumConfig":
        """Create configuration from environment variables."""
        config = cls()

        # Override with environment variables
        config.debug = os.getenv("QUANTUM_DEBUG", "false").lower() == "true"
        config.log_level = os.getenv("QUANTUM_LOG_LEVEL", config.log_level)
        config.max_concurrent_jobs = int(
            os.getenv("QUANTUM_MAX_CONCURRENT_JOobs", config.max_concurrent_jobs)
        )
        config.max_job_queue_size = int(
            os.getenv("QUANTUM_MAX_QUEUE_SIZE", config.max_job_queue_size)
        )
        config.require_authentication = (
            os.getenv("QUANTUM_REQUIRE_AUTH", "true").lower() == "true"
        )
        config.rate_limiting = os.getenv("QUANTUM_RATE_LIMIT", "true").lower() == "true"
        config.rate_limit_per_minute = int(
            os.getenv("QUANTUM_RATE_LIMIT_PER_MINUTE", config.rate_limit_per_minute)
        )

        return config


# Default configuration instance
default_config = QuantumConfig()
