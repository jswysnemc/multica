from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class WorkflowError(Exception):
    pass


class CycleError(WorkflowError):
    pass


class InvalidTransitionError(WorkflowError):
    pass


class FailurePolicy(str, Enum):
    FAIL_FAST = "fail_fast"
    RETRY = "retry"
    SKIP = "skip"


class TaskStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class WorkflowStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


TERMINAL_TASK_STATUSES = {
    TaskStatus.COMPLETED,
    TaskStatus.FAILED,
    TaskStatus.SKIPPED,
    TaskStatus.CANCELLED,
}


@dataclass
class WorkflowTask:
    id: str
    name: str
    failure_policy: FailurePolicy = FailurePolicy.FAIL_FAST
    max_retries: int = 0
    status: TaskStatus = TaskStatus.PENDING
    attempts: int = 0
    output: Any = None
    error: str | None = None

    @property
    def terminal(self) -> bool:
        return self.status in TERMINAL_TASK_STATUSES


class Workflow:
    def __init__(self, workflow_id: str, max_concurrency: int) -> None:
        if max_concurrency <= 0:
            raise ValueError("max_concurrency must be positive")
        self.id = workflow_id
        self.max_concurrency = max_concurrency
        self.status = WorkflowStatus.DRAFT
        self.tasks: dict[str, WorkflowTask] = {}
        self.dependencies: dict[str, set[str]] = {}
        self.dependents: dict[str, set[str]] = {}
        self._order: list[str] = []

    def add_task(
        self,
        task_id: str,
        *,
        name: str = "",
        failure_policy: FailurePolicy | str = FailurePolicy.FAIL_FAST,
        max_retries: int = 0,
    ) -> None:
        self._ensure_draft()
        if not task_id:
            raise ValueError("task_id is required")
        if task_id in self.tasks:
            raise ValueError(f"task already exists: {task_id}")
        if max_retries < 0:
            raise ValueError("max_retries must be non-negative")

        policy = FailurePolicy(failure_policy)
        self.tasks[task_id] = WorkflowTask(
            id=task_id,
            name=name or task_id,
            failure_policy=policy,
            max_retries=max_retries,
        )
        self.dependencies[task_id] = set()
        self.dependents[task_id] = set()
        self._order.append(task_id)

    def add_dependency(self, before_task_id: str, after_task_id: str) -> None:
        self._ensure_draft()
        self._ensure_task(before_task_id)
        self._ensure_task(after_task_id)
        if before_task_id == after_task_id:
            raise CycleError("self dependency is not allowed")

        self.dependencies[after_task_id].add(before_task_id)
        self.dependents[before_task_id].add(after_task_id)
        if self.has_cycle():
            self.dependencies[after_task_id].remove(before_task_id)
            self.dependents[before_task_id].remove(after_task_id)
            raise CycleError(f"dependency creates cycle: {before_task_id} -> {after_task_id}")

    def has_cycle(self) -> bool:
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(task_id: str) -> bool:
            if task_id in visiting:
                return True
            if task_id in visited:
                return False
            visiting.add(task_id)
            for child_id in self.dependents[task_id]:
                if visit(child_id):
                    return True
            visiting.remove(task_id)
            visited.add(task_id)
            return False

        return any(visit(task_id) for task_id in self._order)

    def start(self) -> None:
        self._ensure_draft()
        if not self.tasks:
            raise WorkflowError("workflow must contain at least one task")
        self.status = WorkflowStatus.RUNNING
        self._refresh_ready_tasks()

    def claim_ready(self, limit: int | None = None) -> list[str]:
        if self.status != WorkflowStatus.RUNNING:
            return []
        self._refresh_ready_tasks()
        capacity = self.max_concurrency - self.running_count()
        if limit is not None:
            if limit <= 0:
                return []
            capacity = min(capacity, limit)
        if capacity <= 0:
            return []

        claimed: list[str] = []
        for task_id in self._order:
            if len(claimed) >= capacity:
                break
            task = self.tasks[task_id]
            if task.status != TaskStatus.READY:
                continue
            task.status = TaskStatus.RUNNING
            task.attempts += 1
            claimed.append(task_id)
        return claimed

    def complete_task(self, task_id: str, output: Any = None) -> None:
        task = self._ensure_task(task_id)
        if task.status != TaskStatus.RUNNING:
            raise InvalidTransitionError(f"task is not running: {task_id}")
        task.output = output
        task.status = TaskStatus.COMPLETED
        self._refresh_ready_tasks()

    def fail_task(self, task_id: str, error: str) -> None:
        task = self._ensure_task(task_id)
        if task.status != TaskStatus.RUNNING:
            raise InvalidTransitionError(f"task is not running: {task_id}")

        task.error = error
        if task.failure_policy == FailurePolicy.RETRY and task.attempts <= task.max_retries:
            task.status = TaskStatus.PENDING
            self._refresh_ready_tasks()
            return

        if task.failure_policy == FailurePolicy.SKIP:
            task.status = TaskStatus.SKIPPED
            self._refresh_ready_tasks()
            return

        task.status = TaskStatus.FAILED
        self._cancel_non_terminal_tasks()
        self.status = WorkflowStatus.FAILED

    def cancel(self) -> None:
        if self.status in {WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED}:
            return
        self._cancel_non_terminal_tasks()
        self.status = WorkflowStatus.CANCELLED

    def running_count(self) -> int:
        return sum(1 for task in self.tasks.values() if task.status == TaskStatus.RUNNING)

    def ready_tasks(self) -> list[str]:
        self._refresh_ready_tasks()
        return [task_id for task_id in self._order if self.tasks[task_id].status == TaskStatus.READY]

    def statuses(self) -> dict[str, TaskStatus]:
        return {task_id: self.tasks[task_id].status for task_id in self._order}

    def _refresh_ready_tasks(self) -> None:
        if self.status != WorkflowStatus.RUNNING:
            return

        changed = True
        while changed:
            changed = False
            for task_id in self._order:
                task = self.tasks[task_id]
                if task.status != TaskStatus.PENDING:
                    continue

                deps = self.dependencies[task_id]
                if any(self.tasks[dep_id].status in {TaskStatus.FAILED, TaskStatus.SKIPPED, TaskStatus.CANCELLED} for dep_id in deps):
                    task.status = TaskStatus.SKIPPED
                    changed = True
                    continue

                if all(self.tasks[dep_id].status == TaskStatus.COMPLETED for dep_id in deps):
                    task.status = TaskStatus.READY
                    changed = True

        if all(task.terminal for task in self.tasks.values()):
            if any(task.status == TaskStatus.FAILED for task in self.tasks.values()):
                self.status = WorkflowStatus.FAILED
            else:
                self.status = WorkflowStatus.COMPLETED

    def _cancel_non_terminal_tasks(self) -> None:
        for task in self.tasks.values():
            if not task.terminal:
                task.status = TaskStatus.CANCELLED

    def _ensure_draft(self) -> None:
        if self.status != WorkflowStatus.DRAFT:
            raise InvalidTransitionError("workflow graph cannot change after start")

    def _ensure_task(self, task_id: str) -> WorkflowTask:
        try:
            return self.tasks[task_id]
        except KeyError as exc:
            raise KeyError(f"unknown task: {task_id}") from exc
