"""
Health Check API Endpoints
"""

from fastapi import APIRouter
import sys
sys.path.append('..')
from app.main import get_port_manager, get_suite_communicator

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check"""
    try:
        port_manager = get_port_manager()
        suite_communicator = get_suite_communicator()
        
        return {
            "status": "healthy",
            "service": "iTechSmart Port Manager",
            "version": "1.0.0",
            "components": {
                "port_manager": "active",
                "suite_communicator": "active"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.get("/detailed")
async def detailed_health():
    """Detailed health check with statistics"""
    try:
        port_manager = get_port_manager()
        suite_communicator = get_suite_communicator()
        
        stats = await port_manager.get_port_statistics()
        conflicts = await port_manager.detect_conflicts()
        
        return {
            "status": "healthy",
            "service": "iTechSmart Port Manager",
            "version": "1.0.0",
            "statistics": stats,
            "conflicts": len(conflicts),
            "components": {
                "port_manager": "active",
                "suite_communicator": "active"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }