# 任务三：修复分析报告

## 选择的问题

选择任务一场景 C 中发现的状态一致性问题：Daemon 本地任务执行期间，如果后端将任务改成 `failed`、`completed` 或其他终态，当前本地执行不会立即中断。

## 根因分析

问题集中在 Daemon 的本地执行监控逻辑。

代码路径：

- `server/internal/daemon/daemon.go:2046`：`shouldInterruptAgent`
- `server/internal/daemon/daemon.go:2073`：`watchTaskCancellation`
- `server/internal/daemon/daemon.go:2174`：`handleTask` 启动状态轮询
- `server/internal/daemon/daemon.go:2220`：完成前最后一次状态检查
- `server/internal/daemon/client.go:269`：`GetTaskStatus`

当前 `shouldInterruptAgent` 只在两种情况下中断：

- 服务端返回 `status == "cancelled"`。
- 查询 task 状态返回 404。

这覆盖了用户取消、任务删除等路径，但没有覆盖 `failed`、`completed`、`skipped` 等非 active 终态。因此，当服务端 sweeper、管理员操作或其他修复流程将任务改为终态时，本地 Agent 仍可能继续运行。运行结束后，服务端 `CompleteAgentTask` 又会因为 SQL 只允许 `status='running'` 而拒绝完成写入。

## 方案选择

采用保守的本地中断策略：

```text
active status: dispatched, waiting_local_directory, running
terminal or unexpected status: interrupt
transient HTTP error: do not interrupt
404 task not found: interrupt
```

原因：

- 本地 Agent 已经在执行时，服务端视角下 task 应当仍处于 active 状态。
- 如果服务端返回终态，说明服务端已经不再期待该本地执行继续。
- 对 5xx、网络错误等瞬时错误保持不取消，避免网络抖动误杀任务。

进一步优化：维护本地 active task cancel registry，在 WebSocket 重连后立即对账所有本地 active task，而不是完全等待 5 秒轮询。

## 关键修复 diff

```diff
diff --git a/server/internal/daemon/daemon.go b/server/internal/daemon/daemon.go
@@
 func shouldInterruptAgent(status string, err error) bool {
     if err != nil {
         return isTaskNotFoundError(err)
     }
-    return status == "cancelled"
+    switch status {
+    case "", "dispatched", "waiting_local_directory", "running":
+        return false
+    default:
+        return true
+    }
 }
```

```diff
diff --git a/server/internal/daemon/daemon.go b/server/internal/daemon/daemon.go
@@
 type Daemon struct {
@@
     activeTasks atomic.Int64
+    activeTaskMu      sync.Mutex
+    activeTaskCancels map[string]context.CancelFunc
 }
```

```diff
diff --git a/server/internal/daemon/daemon.go b/server/internal/daemon/daemon.go
@@
     runCtx, runCancel := context.WithCancel(ctx)
     defer runCancel()
+    d.trackActiveTask(task.ID, runCancel)
+    defer d.untrackActiveTask(task.ID)
```

```diff
diff --git a/server/internal/daemon/wakeup.go b/server/internal/daemon/wakeup.go
@@
     d.logger.Info("task wakeup websocket connected", "runtimes", len(runtimeIDs))
     signalTaskWakeup(taskWakeups)
+    go d.reconcileActiveTasks(ctx)
```

## 验证方式

### 单元测试

新增 `shouldInterruptAgent` 表驱动测试：

```text
status=cancelled, err=nil -> true
status=failed, err=nil -> true
status=completed, err=nil -> true
status=skipped, err=nil -> true
status=unknown, err=nil -> true
status=running, err=nil -> false
status=dispatched, err=nil -> false
status=waiting_local_directory, err=nil -> false
status="", err=nil -> false
err=task not found -> true
err=transient 500 -> false
```

新增 `watchTaskCancellation` 测试：

- mock `GetTaskStatus` 返回 `failed`。
- 断言 cancellation channel 关闭。
- mock `GetTaskStatus` 返回 5xx。
- 断言 cancellation channel 不关闭。

新增重连对账测试：

- 注册一个 active task 的 cancel function。
- mock `GetTaskStatus` 返回 `failed`。
- 调用 `reconcileActiveTasks`。
- 断言 cancel function 被调用。

### 集成测试

构造任务从 `running` 被服务端改成 `failed` 的场景：

1. daemon claim task。
2. daemon start task。
3. runner 阻塞等待 context。
4. 测试中将 task 状态更新为 `failed`。
5. 等待状态轮询触发。
6. 断言 runner 收到取消。
7. 断言 daemon 不调用 `CompleteTask`。

### 回归验证

运行：

```bash
go test ./server/internal/daemon -run 'TestShouldInterruptAgent|TestWatchTaskCancellation|TestReconnectReconcile'
go test ./server/internal/handler -run TestClaimTask
```

## 风险评估

- 误杀风险：如果服务端短暂返回未知新状态，本地会中断。该风险可接受，因为未知状态不应被当作 active。为兼容未来扩展，可以将 active 状态集中定义为常量并在新增状态时同步更新测试。
- 重连对账压力：每次 WS 连接成功会查询本地 active task 状态。active task 数受 daemon 并发限制控制，默认规模很小，压力可控。
- 与取消路径兼容：原有 `cancelled` 和 404 语义保持不变。

## PR 状态

已创建 Pull Request：

```text
https://github.com/multica-ai/multica/pull/3814
```

对应 fork 分支：

```text
https://github.com/jswysnemc/multica/tree/fix/daemon-terminal-status-interrupt
```

本地验证已执行：

```bash
go test ./internal/daemon -run 'TestShouldInterruptAgent|TestWatchTaskCancellation'
python3 -m unittest discover -s submission/task2/src -p 'test_*.py'
```
