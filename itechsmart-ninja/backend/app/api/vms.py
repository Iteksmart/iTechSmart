"""
Virtual Machine Pool API Routes
Provides endpoints for managing concurrent VMs
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.database import User, VirtualMachine, VMExecution
from app.integrations.vm_pool_manager import VMPoolManager

router = APIRouter(prefix="/api/vms", tags=["vms"])

# Initialize VM pool manager
vm_pool = VMPoolManager(max_vms_per_user=10, max_total_vms=100)


@router.post("/create")
async def create_vm(
    name: str,
    language: str,
    cpu_limit: float = 1.0,
    memory_limit: int = 512,
    disk_limit: int = 1024,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new virtual machine
    
    Args:
        name: VM name
        language: Programming language (python, nodejs, java, go, rust, ruby, php, dotnet)
        cpu_limit: CPU cores limit
        memory_limit: Memory limit in MB
        disk_limit: Disk limit in MB
    """
    try:
        # Create VM in pool
        vm_info = await vm_pool.create_vm(
            user_id=current_user.id,
            name=name,
            language=language,
            cpu_limit=cpu_limit,
            memory_limit=memory_limit,
            disk_limit=disk_limit
        )
        
        # Save to database
        vm_db = VirtualMachine(
            user_id=current_user.id,
            vm_id=vm_info['id'],
            name=name,
            language=language,
            status='running',
            container_id=vm_info.get('container_id'),
            cpu_limit=cpu_limit,
            memory_limit=memory_limit,
            disk_limit=disk_limit,
            started_at=datetime.utcnow()
        )
        db.add(vm_db)
        db.commit()
        db.refresh(vm_db)
        
        return {
            "success": True,
            "vm": {
                "id": vm_db.id,
                "vm_id": vm_info['id'],
                "name": name,
                "language": language,
                "status": "running",
                "cpu_limit": cpu_limit,
                "memory_limit": memory_limit,
                "disk_limit": disk_limit,
                "created_at": vm_db.created_at.isoformat() if vm_db.created_at else None
            },
            "message": "VM created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
async def list_vms(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all VMs for current user"""
    try:
        vms = db.query(VirtualMachine).filter(
            VirtualMachine.user_id == current_user.id
        ).offset(skip).limit(limit).all()
        
        vm_list = []
        for vm in vms:
            vm_list.append({
                "id": vm.id,
                "vm_id": vm.vm_id,
                "name": vm.name,
                "language": vm.language,
                "status": vm.status,
                "cpu_limit": vm.cpu_limit,
                "memory_limit": vm.memory_limit,
                "created_at": vm.created_at.isoformat() if vm.created_at else None,
                "started_at": vm.started_at.isoformat() if vm.started_at else None
            })
        
        return {
            "success": True,
            "vms": vm_list,
            "total": len(vm_list),
            "limit": vm_pool.max_vms_per_user,
            "message": "VMs retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{vm_id}")
async def get_vm(
    vm_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get VM details"""
    try:
        vm = db.query(VirtualMachine).filter(
            VirtualMachine.vm_id == vm_id,
            VirtualMachine.user_id == current_user.id
        ).first()
        
        if not vm:
            raise HTTPException(status_code=404, detail="VM not found")
        
        # Get status from pool
        try:
            status_info = await vm_pool.get_vm_status(vm_id)
        except:
            status_info = {}
        
        return {
            "success": True,
            "vm": {
                "id": vm.id,
                "vm_id": vm.vm_id,
                "name": vm.name,
                "language": vm.language,
                "status": vm.status,
                "cpu_limit": vm.cpu_limit,
                "memory_limit": vm.memory_limit,
                "disk_limit": vm.disk_limit,
                "container_id": vm.container_id,
                "created_at": vm.created_at.isoformat() if vm.created_at else None,
                "started_at": vm.started_at.isoformat() if vm.started_at else None,
                "stopped_at": vm.stopped_at.isoformat() if vm.stopped_at else None,
                "stats": status_info.get('stats', {}),
                "execution_count": status_info.get('execution_count', 0)
            },
            "message": "VM retrieved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{vm_id}")
async def delete_vm(
    vm_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete VM"""
    try:
        vm = db.query(VirtualMachine).filter(
            VirtualMachine.vm_id == vm_id,
            VirtualMachine.user_id == current_user.id
        ).first()
        
        if not vm:
            raise HTTPException(status_code=404, detail="VM not found")
        
        # Delete from pool
        await vm_pool.delete_vm(vm_id)
        
        # Delete from database
        db.delete(vm)
        db.commit()
        
        return {
            "success": True,
            "message": "VM deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{vm_id}/start")
async def start_vm(
    vm_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start VM"""
    try:
        vm = db.query(VirtualMachine).filter(
            VirtualMachine.vm_id == vm_id,
            VirtualMachine.user_id == current_user.id
        ).first()
        
        if not vm:
            raise HTTPException(status_code=404, detail="VM not found")
        
        # Start in pool
        await vm_pool.start_vm(vm_id)
        
        # Update database
        vm.status = 'running'
        vm.started_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "message": "VM started successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{vm_id}/stop")
async def stop_vm(
    vm_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stop VM"""
    try:
        vm = db.query(VirtualMachine).filter(
            VirtualMachine.vm_id == vm_id,
            VirtualMachine.user_id == current_user.id
        ).first()
        
        if not vm:
            raise HTTPException(status_code=404, detail="VM not found")
        
        # Stop in pool
        await vm_pool.stop_vm(vm_id)
        
        # Update database
        vm.status = 'stopped'
        vm.stopped_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "message": "VM stopped successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{vm_id}/restart")
async def restart_vm(
    vm_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Restart VM"""
    try:
        vm = db.query(VirtualMachine).filter(
            VirtualMachine.vm_id == vm_id,
            VirtualMachine.user_id == current_user.id
        ).first()
        
        if not vm:
            raise HTTPException(status_code=404, detail="VM not found")
        
        # Restart in pool
        await vm_pool.restart_vm(vm_id)
        
        # Update database
        vm.status = 'running'
        vm.started_at = datetime.utcnow()
        db.commit()
        
        return {
            "success": True,
            "message": "VM restarted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{vm_id}/execute")
async def execute_in_vm(
    vm_id: str,
    code: str,
    timeout: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute code in VM"""
    try:
        vm = db.query(VirtualMachine).filter(
            VirtualMachine.vm_id == vm_id,
            VirtualMachine.user_id == current_user.id
        ).first()
        
        if not vm:
            raise HTTPException(status_code=404, detail="VM not found")
        
        # Execute in pool
        result = await vm_pool.execute_in_vm(vm_id, code, timeout)
        
        # Save execution to database
        execution = VMExecution(
            vm_id=vm.id,
            code=code,
            output=result['output'],
            error=result['error'],
            exit_code=result['exit_code'],
            execution_time=result['execution_time']
        )
        db.add(execution)
        db.commit()
        
        return {
            "success": True,
            "result": result,
            "message": "Code executed successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{vm_id}/status")
async def get_vm_status(
    vm_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get VM status"""
    try:
        vm = db.query(VirtualMachine).filter(
            VirtualMachine.vm_id == vm_id,
            VirtualMachine.user_id == current_user.id
        ).first()
        
        if not vm:
            raise HTTPException(status_code=404, detail="VM not found")
        
        # Get status from pool
        status_info = await vm_pool.get_vm_status(vm_id)
        
        return {
            "success": True,
            "status": status_info,
            "message": "VM status retrieved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{vm_id}/logs")
async def get_vm_logs(
    vm_id: str,
    tail: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get VM logs"""
    try:
        vm = db.query(VirtualMachine).filter(
            VirtualMachine.vm_id == vm_id,
            VirtualMachine.user_id == current_user.id
        ).first()
        
        if not vm:
            raise HTTPException(status_code=404, detail="VM not found")
        
        # Get logs from pool
        logs = await vm_pool.get_vm_logs(vm_id, tail)
        
        return {
            "success": True,
            "logs": logs,
            "message": "VM logs retrieved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-execute")
async def batch_execute(
    vm_ids: List[str],
    code: str,
    timeout: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Execute code in multiple VMs"""
    try:
        # Verify all VMs belong to user
        vms = db.query(VirtualMachine).filter(
            VirtualMachine.vm_id.in_(vm_ids),
            VirtualMachine.user_id == current_user.id
        ).all()
        
        if len(vms) != len(vm_ids):
            raise HTTPException(status_code=404, detail="One or more VMs not found")
        
        # Execute in pool
        results = await vm_pool.batch_execute(vm_ids, code, timeout)
        
        # Save executions to database
        for result in results:
            vm = next((v for v in vms if v.vm_id == result['vm_id']), None)
            if vm:
                execution = VMExecution(
                    vm_id=vm.id,
                    code=code,
                    output=result['output'],
                    error=result['error'],
                    exit_code=result['exit_code'],
                    execution_time=result['execution_time']
                )
                db.add(execution)
        
        db.commit()
        
        successful = sum(1 for r in results if r['exit_code'] == 0)
        
        return {
            "success": True,
            "results": results,
            "total": len(results),
            "successful": successful,
            "failed": len(results) - successful,
            "message": f"Batch execution completed: {successful}/{len(results)} successful"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pool-status")
async def get_pool_status(
    current_user: User = Depends(get_current_user)
):
    """Get VM pool status"""
    try:
        status = await vm_pool.get_pool_status()
        
        return {
            "success": True,
            "pool_status": status,
            "message": "Pool status retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup")
async def cleanup_inactive_vms(
    max_age_hours: int = Query(24, ge=1, le=168),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cleanup inactive VMs (admin only)"""
    try:
        # Check if user is admin
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Cleanup in pool
        cleaned_count = await vm_pool.cleanup_inactive_vms(max_age_hours)
        
        return {
            "success": True,
            "cleaned_count": cleaned_count,
            "message": f"Cleaned up {cleaned_count} inactive VMs"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))