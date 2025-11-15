# Feature 9: Scheduled Tasks - Complete Specification

## Overview
Cron-like task scheduling system for automated execution of code, scripts, and workflows at specified times or intervals.

---

## Capabilities

### Scheduling Options
- **Cron expressions** - Standard cron syntax
- **Intervals** - Every N minutes/hours/days
- **One-time** - Execute once at specific time
- **Recurring** - Daily, weekly, monthly
- **Conditional** - Execute based on conditions

### Features
- Task history and logs
- Email notifications on completion/failure
- Retry on failure (configurable)
- Task dependencies
- Parallel execution
- Resource limits per task
- Task templates

---

## API Endpoints

```
POST   /api/scheduler/tasks/create
GET    /api/scheduler/tasks
GET    /api/scheduler/tasks/{task_id}
PUT    /api/scheduler/tasks/{task_id}
DELETE /api/scheduler/tasks/{task_id}
POST   /api/scheduler/tasks/{task_id}/enable
POST   /api/scheduler/tasks/{task_id}/disable
POST   /api/scheduler/tasks/{task_id}/run-now
GET    /api/scheduler/tasks/{task_id}/history
GET    /api/scheduler/tasks/{task_id}/logs
GET    /api/scheduler/next-runs
```

---

## Database Models

```python
class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    description = Column(Text)
    schedule = Column(String)  # Cron expression
    code = Column(Text)
    language = Column(String)
    enabled = Column(Boolean, default=True)
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    timeout = Column(Integer)  # seconds
    created_at = Column(DateTime)

class TaskExecution(Base):
    __tablename__ = "task_executions"
    
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("scheduled_tasks.id"))
    status = Column(String)  # success, failure, running
    output = Column(Text)
    error = Column(Text)
    execution_time = Column(Float)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
```

---

## VS Code Commands

1. `iTechSmart: Create Scheduled Task`
2. `iTechSmart: List Scheduled Tasks`
3. `iTechSmart: Edit Scheduled Task`
4. `iTechSmart: Enable/Disable Task`
5. `iTechSmart: Run Task Now`
6. `iTechSmart: View Task History`

---

## Terminal Commands

```bash
schedule create <name>      # Create task
schedule list              # List tasks
schedule enable <id>       # Enable task
schedule disable <id>      # Disable task
schedule run <id>          # Run now
schedule history <id>      # View history
```

---

## Implementation Steps

**Total Time**: 5-6 hours

### Phase 1: Backend (4 hours)
1. Create `task_scheduler.py` (2 hours)
2. Create `scheduler.py` API (1 hour)
3. Add database models (30 min)
4. Add background worker (30 min)

### Phase 2: Frontend (1 hour)
1. Create `schedulerCommands.ts`

### Phase 3: Testing (1 hour)

---

## Dependencies

```
APScheduler>=3.10.0
croniter>=2.0.0
celery>=5.3.0  # Optional for distributed tasks
```

---

## Example Usage

```python
# Create scheduled task
task = await create_scheduled_task(
    name="Daily Backup",
    schedule="0 2 * * *",  # 2 AM daily
    code="backup_database()",
    language="python"
)

# Run immediately
await run_task_now(task.id)
```

---

## Status

**Specification**: ✅ Complete
**Skeleton Code**: ✅ Provided
**Implementation**: ⏳ Pending
**Estimated Time**: 5-6 hours