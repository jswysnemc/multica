import unittest

from workflow_engine import CycleError, FailurePolicy, TaskStatus, Workflow, WorkflowStatus


class WorkflowEngineTest(unittest.TestCase):
    def test_simple_linear_dependency(self) -> None:
        workflow = Workflow("linear", max_concurrency=3)
        for task_id in ["A", "B", "C"]:
            workflow.add_task(task_id)
        workflow.add_dependency("A", "B")
        workflow.add_dependency("B", "C")

        workflow.start()

        self.assertEqual(workflow.claim_ready(), ["A"])
        workflow.complete_task("A")
        self.assertEqual(workflow.claim_ready(), ["B"])
        workflow.complete_task("B")
        self.assertEqual(workflow.claim_ready(), ["C"])
        workflow.complete_task("C")

        self.assertEqual(workflow.status, WorkflowStatus.COMPLETED)

    def test_parallel_execution_a_to_b_c_to_d(self) -> None:
        workflow = Workflow("parallel", max_concurrency=3)
        for task_id in ["A", "B", "C", "D"]:
            workflow.add_task(task_id)
        workflow.add_dependency("A", "B")
        workflow.add_dependency("A", "C")
        workflow.add_dependency("B", "D")
        workflow.add_dependency("C", "D")

        workflow.start()
        self.assertEqual(workflow.claim_ready(), ["A"])
        workflow.complete_task("A")

        claimed = workflow.claim_ready()
        self.assertEqual(set(claimed), {"B", "C"})
        self.assertEqual(workflow.running_count(), 2)

        workflow.complete_task("B")
        self.assertEqual(workflow.claim_ready(), [])
        workflow.complete_task("C")
        self.assertEqual(workflow.claim_ready(), ["D"])
        workflow.complete_task("D")

        self.assertEqual(workflow.status, WorkflowStatus.COMPLETED)

    def test_diamond_dependency(self) -> None:
        workflow = Workflow("diamond", max_concurrency=2)
        for task_id in ["A", "B", "C", "D", "E"]:
            workflow.add_task(task_id)
        workflow.add_dependency("A", "B")
        workflow.add_dependency("A", "C")
        workflow.add_dependency("B", "D")
        workflow.add_dependency("C", "D")
        workflow.add_dependency("D", "E")

        workflow.start()
        self.assertEqual(workflow.claim_ready(), ["A"])
        workflow.complete_task("A")
        self.assertEqual(set(workflow.claim_ready()), {"B", "C"})
        workflow.complete_task("B")
        workflow.complete_task("C")
        self.assertEqual(workflow.claim_ready(), ["D"])
        workflow.complete_task("D")
        self.assertEqual(workflow.claim_ready(), ["E"])
        workflow.complete_task("E")

        self.assertEqual(workflow.status, WorkflowStatus.COMPLETED)

    def test_cycle_detection(self) -> None:
        workflow = Workflow("cycle", max_concurrency=2)
        for task_id in ["A", "B", "C"]:
            workflow.add_task(task_id)
        workflow.add_dependency("A", "B")
        workflow.add_dependency("B", "C")

        with self.assertRaises(CycleError):
            workflow.add_dependency("C", "A")

        self.assertFalse(workflow.has_cycle())

    def test_fail_fast_policy(self) -> None:
        workflow = Workflow("fail-fast", max_concurrency=2)
        workflow.add_task("A", failure_policy=FailurePolicy.FAIL_FAST)
        workflow.add_task("B")
        workflow.add_task("C")
        workflow.add_dependency("A", "C")

        workflow.start()
        self.assertEqual(set(workflow.claim_ready()), {"A", "B"})
        workflow.fail_task("A", "boom")

        self.assertEqual(workflow.status, WorkflowStatus.FAILED)
        self.assertEqual(workflow.tasks["A"].status, TaskStatus.FAILED)
        self.assertEqual(workflow.tasks["B"].status, TaskStatus.CANCELLED)
        self.assertEqual(workflow.tasks["C"].status, TaskStatus.CANCELLED)

    def test_retry_policy(self) -> None:
        workflow = Workflow("retry", max_concurrency=1)
        workflow.add_task("A", failure_policy=FailurePolicy.RETRY, max_retries=2)

        workflow.start()
        self.assertEqual(workflow.claim_ready(), ["A"])
        workflow.fail_task("A", "first failure")
        self.assertEqual(workflow.tasks["A"].status, TaskStatus.READY)
        self.assertEqual(workflow.tasks["A"].attempts, 1)

        self.assertEqual(workflow.claim_ready(), ["A"])
        workflow.fail_task("A", "second failure")
        self.assertEqual(workflow.tasks["A"].status, TaskStatus.READY)
        self.assertEqual(workflow.tasks["A"].attempts, 2)

        self.assertEqual(workflow.claim_ready(), ["A"])
        workflow.complete_task("A")

        self.assertEqual(workflow.tasks["A"].attempts, 3)
        self.assertEqual(workflow.status, WorkflowStatus.COMPLETED)

    def test_skip_policy(self) -> None:
        workflow = Workflow("skip", max_concurrency=2)
        workflow.add_task("A", failure_policy=FailurePolicy.SKIP)
        workflow.add_task("B")
        workflow.add_task("C")
        workflow.add_dependency("A", "B")

        workflow.start()
        self.assertEqual(set(workflow.claim_ready()), {"A", "C"})
        workflow.fail_task("A", "non-critical failure")

        self.assertEqual(workflow.tasks["A"].status, TaskStatus.SKIPPED)
        self.assertEqual(workflow.tasks["B"].status, TaskStatus.SKIPPED)
        self.assertEqual(workflow.tasks["C"].status, TaskStatus.RUNNING)

        workflow.complete_task("C")
        self.assertEqual(workflow.status, WorkflowStatus.COMPLETED)

    def test_retry_exhaustion_escalates_to_fail_fast(self) -> None:
        workflow = Workflow("retry-exhausted", max_concurrency=2)
        workflow.add_task("A", failure_policy=FailurePolicy.RETRY, max_retries=1)
        workflow.add_task("B")

        workflow.start()
        self.assertEqual(set(workflow.claim_ready()), {"A", "B"})
        workflow.fail_task("A", "first failure")
        self.assertEqual(workflow.tasks["A"].status, TaskStatus.READY)

        self.assertEqual(workflow.claim_ready(), ["A"])
        workflow.fail_task("A", "second failure")

        self.assertEqual(workflow.status, WorkflowStatus.FAILED)
        self.assertEqual(workflow.tasks["A"].status, TaskStatus.FAILED)
        self.assertEqual(workflow.tasks["B"].status, TaskStatus.CANCELLED)

    def test_concurrency_limit(self) -> None:
        workflow = Workflow("limit", max_concurrency=3)
        for index in range(10):
            workflow.add_task(f"T{index}")

        workflow.start()
        self.assertEqual(workflow.claim_ready(limit=10), ["T0", "T1", "T2"])
        self.assertEqual(workflow.running_count(), 3)
        self.assertEqual(workflow.claim_ready(limit=10), [])

        workflow.complete_task("T0")
        self.assertEqual(workflow.claim_ready(limit=10), ["T3"])
        self.assertEqual(workflow.running_count(), 3)

        for task_id in ["T1", "T2", "T3"]:
            workflow.complete_task(task_id)
        self.assertEqual(workflow.claim_ready(limit=10), ["T4", "T5", "T6"])


if __name__ == "__main__":
    unittest.main()
