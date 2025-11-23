"""
iTechSmart Quantum Computing API

REST API endpoints for quantum computing services.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime

from app.services.quantum_computing_service import (
    QuantumComputingService, 
    get_quantum_service,
    QuantumAlgorithm,
    QuantumBackend
)
from app.models.quantum import (
    QuantumCircuit,
    QuantumResult,
    OptimizationProblem,
    QuantumJob
)
from app.core.quantum_config import QuantumConfig


router = APIRouter(
    prefix="/api/v1/quantum",
    tags=["quantum-computing"]
)


@router.get("/status")
async def get_quantum_status(
    service: QuantumComputingService = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """Get quantum computing service status."""
    return service.get_backend_info()


@router.get("/backends")
async def list_backends(
    service: QuantumComputingService = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """List available quantum backends."""
    backend_info = service.get_backend_info()
    return {
        "backends": backend_info["available_backends"],
        "total_available": len([b for b in backend_info["available_backends"] if b["available"]])
    }


@router.post("/optimization")
async def create_optimization_problem(
    objective_function: str,
    variables: List[str],
    constraints: List[Dict[str, Any]],
    service: QuantumComputingService = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """Create a quantum optimization problem."""
    try:
        problem = await service.create_optimization_problem(
            objective_function, variables, constraints
        )
        return {
            "success": True,
            "problem": problem.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/optimization/solve")
async def solve_optimization(
    problem_id: str,
    backend: str = "simulator",
    algorithm: str = "qaoa_optimization",
    service: QuantumComputingService = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """Solve an optimization problem using quantum computing."""
    try:
        # Convert string parameters to enums
        quantum_backend = QuantumBackend(backend)
        quantum_algorithm = QuantumAlgorithm(algorithm)
        
        # For demo, create a simple optimization problem
        problem = await service.create_optimization_problem(
            "minimize x1 + x2",
            ["x1", "x2"],
            [{"type": "linear", "coefficients": {"x1": 1, "x2": 1}, "sense": "==", "rhs": 1}]
        )
        
        result = await service.solve_optimization(
            problem, quantum_backend, quantum_algorithm
        )
        
        return {
            "success": True,
            "result": result.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/circuit/grover")
async def create_grover_search(
    search_space_size: int,
    target_states: List[int],
    iterations: Optional[int] = None,
    service: QuantumComputingService = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """Create Grover's search algorithm circuit."""
    try:
        circuit = await service.create_grover_search(
            search_space_size, target_states, iterations
        )
        return {
            "success": True,
            "circuit": circuit.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/circuit/execute")
async def execute_circuit(
    circuit_id: str,
    backend: str = "simulator",
    shots: int = 1024,
    service: QuantumComputingService = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """Execute a quantum circuit."""
    try:
        # Create a simple Grover circuit for demo
        circuit = await service.create_grover_search(8, [3, 5])
        
        quantum_backend = QuantumBackend(backend)
        result = await service.execute_circuit(circuit, quantum_backend, shots)
        
        return {
            "success": True,
            "result": result.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/jobs")
async def list_jobs(
    status: Optional[str] = None,
    service: QuantumComputingService = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """List quantum computing jobs."""
    jobs = service.list_jobs(status)
    return {
        "jobs": [job.to_dict() for job in jobs],
        "total": len(jobs)
    }


@router.get("/jobs/{job_id}")
async def get_job(
    job_id: str,
    service: QuantumComputingService = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """Get specific quantum job details."""
    job = service.get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job": job.to_dict()
    }


@router.delete("/jobs/{job_id}")
async def cancel_job(
    job_id: str,
    service: QuantumComputingService = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """Cancel a quantum job."""
    job = service.get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.is_finished():
        raise HTTPException(status_code=400, detail="Job cannot be cancelled")
    
    # Update job status to cancelled
    job.status = "cancelled"
    job.completed_at = datetime.now()
    
    return {
        "success": True,
        "message": "Job cancelled successfully"
    }


@router.get("/algorithms")
async def list_algorithms(
    service: QuantumComputingService = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """List available quantum algorithms."""
    backend_info = service.get_backend_info()
    
    algorithms = [
        {
            "name": "Grover's Search",
            "id": "grover_search",
            "description": "Unstructured search algorithm providing quadratic speedup",
            "complexity": "O(√N)",
            "applications": ["database search", "cryptanalysis", "optimization"],
            "qubits_required": "log₂N where N is search space size"
        },
        {
            "name": "QAOA Optimization",
            "id": "qaoa_optimization",
            "description": "Quantum Approximate Optimization Algorithm for combinatorial optimization",
            "complexity": "O(poly(n))",
            "applications": ["portfolio optimization", "routing", "scheduling"],
            "qubits_required": "n (number of variables)"
        },
        {
            "name": "VQE Eigenvalue",
            "id": "vqe_eigenvalue",
            "description": "Variational Quantum Eigensolver for finding eigenvalues of matrices",
            "complexity": "O(poly(n))",
            "applications": ["quantum chemistry", "materials science", "physics"],
            "qubits_required": "n (system size)"
        },
        {
            "name": "Quantum Machine Learning",
            "id": "quantum_ml",
            "description": "Quantum algorithms for machine learning tasks",
            "complexity": "Problem dependent",
            "applications": ["classification", "clustering", "regression"],
            "qubits_required": "Variable (typically 4-16 for demos)"
        },
        {
            "name": "Quantum Monte Carlo",
            "id": "quantum_monte_carlo",
            "description": "Quantum-enhanced Monte Carlo simulation",
            "complexity": "O(1/√ε) quadratic speedup",
            "applications": ["finance", "risk analysis", "simulation"],
            "qubits_required": "8-32 depending on problem complexity"
        }
    ]
    
    return {
        "algorithms": algorithms,
        "qiskit_available": backend_info.get("qiskit_available", False)
    }


@router.get("/applications")
async def list_applications(
    domain: Optional[str] = None,
    service: QuantumComputingService = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """List quantum computing applications."""
    applications = [
        {
            "name": "Portfolio Optimization",
            "domain": "finance",
            "algorithm": "qaoa_optimization",
            "description": "Optimize investment portfolios for maximum return and minimum risk",
            "complexity": "Medium",
            "expected_speedup": "Quadratic",
            "qubits_required": "16-64",
            "current_status": "Experimental"
        },
        {
            "name": "Drug Discovery",
            "domain": "healthcare",
            "algorithm": "vqe_eigenvalue",
            "description": "Simulate molecular interactions for drug development",
            "complexity": "High",
            "expected_speedup": "Exponential",
            "qubits_required": "50-100",
            "current_status": "Early research"
        },
        {
            "name": "Supply Chain Optimization",
            "domain": "logistics",
            "algorithm": "qaoa_optimization",
            "description": "Optimize routing and inventory management",
            "complexity": "Medium",
            "expected_speedup": "Quadratic",
            "qubits_required": "32-128",
            "current_status": "Pilot studies"
        },
        {
            "name": "Cryptographic Analysis",
            "domain": "security",
            "algorithm": "grover_search",
            "description": "Analyze cryptographic protocols and vulnerabilities",
            "complexity": "Low to Medium",
            "expected_speedup": "Quadratic",
            "qubits_required": "8-32",
            "current_status": "Research"
        },
        {
            "name": "Financial Risk Analysis",
            "domain": "finance",
            "algorithm": "quantum_monte_carlo",
            "description": "Monte Carlo simulation for financial risk assessment",
            "complexity": "Medium",
            "expected_speedup": "Quadratic",
            "qubits_required": "16-64",
            "current_status": "Proof of concept"
        }
    ]
    
    if domain:
        applications = [app for app in applications if app["domain"] == domain]
    
    return {
        "applications": applications,
        "total": len(applications)
    }


@router.get("/benchmarks")
async def get_benchmarks(
    service: QuantumComputingService = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """Get quantum algorithm benchmark results."""
    # Mock benchmark data
    benchmarks = [
        {
            "algorithm": "grover_search",
            "backend": "simulator",
            "problem_size": 16,
            "execution_time": 0.05,
            "success_rate": 0.98,
            "accuracy": 0.95,
            "benchmark_date": datetime.now().isoformat()
        },
        {
            "algorithm": "qaoa_optimization",
            "backend": "simulator",
            "problem_size": 8,
            "execution_time": 0.15,
            "success_rate": 0.92,
            "accuracy": 0.88,
            "benchmark_date": datetime.now().isoformat()
        },
        {
            "algorithm": "vqe_eigenvalue",
            "backend": "simulator",
            "problem_size": 4,
            "execution_time": 0.12,
            "success_rate": 0.95,
            "accuracy": 0.91,
            "benchmark_date": datetime.now().isoformat()
        }
    ]
    
    return {
        "benchmarks": benchmarks,
        "last_updated": datetime.now().isoformat()
    }


@router.get("/resources")
async def get_resources(
    service: QuantumComputingService = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """Get quantum computing resource information."""
    backend_info = service.get_backend_info()
    
    return {
        "total_jobs": backend_info.get("total_jobs", 0),
        "active_jobs": backend_info.get("active_jobs", 0),
        "available_backends": len([b for b in backend_info.get("available_backends", []) if b["available"]]),
        "qiskit_available": backend_info.get("qiskit_available", False),
        "service_status": "healthy" if backend_info.get("qiskit_available", True) else "limited"
    }


@router.post("/demo/grover")
async def demo_grover_search(
    service: QuantumComputingService = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """Demo: Run Grover's search algorithm."""
    try:
        # Create a simple search problem
        search_space_size = 16
        target_states = [3, 7, 11]
        
        # Create circuit
        circuit = await service.create_grover_search(
            search_space_size, target_states
        )
        
        # Execute circuit
        result = await service.execute_circuit(
            circuit, QuantumBackend.SIMULATOR, shots=1024
        )
        
        return {
            "success": True,
            "demo_info": {
                "algorithm": "Grover's Search",
                "search_space_size": search_space_size,
                "target_states": target_states,
                "description": f"Search for states {target_states} in a space of {search_space_size} possibilities"
            },
            "circuit": circuit.to_dict(),
            "result": result.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/demo/optimization")
async def demo_optimization(
    service: QuantumComputingService = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """Demo: Run quantum optimization."""
    try:
        # Create optimization problem
        problem = await service.create_optimization_problem(
            "minimize x1 + x2 + x3 + x4",
            ["x1", "x2", "x3", "x4"],
            [
                {"type": "linear", "coefficients": {"x1": 1, "x2": 1}, "sense": ">=", "rhs": 1},
                {"type": "linear", "coefficients": {"x3": 1, "x4": 1}, "sense": ">=", "rhs": 1}
            ]
        )
        
        # Solve optimization
        result = await service.solve_optimization(
            problem, QuantumBackend.SIMULATOR, QuantumAlgorithm.QAOA_OPTIMIZATION
        )
        
        return {
            "success": True,
            "demo_info": {
                "algorithm": "QAOA Optimization",
                "problem_type": "Binary optimization",
                "variables": 4,
                "constraints": 2,
                "description": "Find optimal binary values for 4 variables with constraints"
            },
            "problem": problem.to_dict(),
            "result": result.to_dict()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check(
    service: QuantumComputingService = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """Health check endpoint."""
    backend_info = service.get_backend_info()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "iTechSmart Quantum Computing",
        "qiskit_available": backend_info.get("qiskit_available", False),
        "available_backends": len([b for b in backend_info.get("available_backends", []) if b["available"]]),
        "active_jobs": backend_info.get("active_jobs", 0)
    }