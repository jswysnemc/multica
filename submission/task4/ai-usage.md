# 任务四：AI 工作流

## 4.1 AI 编程工具配置

### 项目指令

配置文件：

- `CLAUDE.md`
- `AGENTS.md`
- `.github/copilot-instructions.md` 或同类仓库级指令

解决的问题：

- 固化项目架构边界，例如 `packages/core`、`packages/ui`、`packages/views` 的依赖方向。
- 约束状态管理策略，例如服务端状态归 React Query，客户端状态归 Zustand。
- 统一提交、注释、翻译和代码风格，减少工具输出和项目规范冲突。

生效场景：

- 阅读陌生模块前，先读取项目根指令。
- 修改跨包代码前，检查 package boundary。
- 写中文文档或 UI 文案前，检查术语和语气规范。

迭代优化：

- 把高频错误写成硬规则，例如 API 响应必须 parse，不直接 cast。
- 把跨端差异写清楚，例如 mobile 只共享类型和纯函数。
- 把命令写入项目指令，避免工具猜测测试和构建命令。

### 全局配置

配置文件示例：

- `task4/ai-configs/codex-config.example.toml`

解决的问题：

- 约束默认工作目录、权限和网络行为。
- 明确优先使用项目内检索工具，而不是直接全仓搜索。
- 将常用模型、审批策略和命令习惯固定下来。

生效场景：

- 日常修复 bug。
- 阅读大型代码库。
- 编写测试和运行验证。

迭代优化：

- 默认不使用破坏性 Git 命令。
- 对网络搜索和源码搜索做工具分层。
- 对文件编辑强制使用补丁，降低误改风险。

### 自定义 Skills

配置文件示例：

- `task4/ai-configs/code-search-skill.example.md`

解决的问题：

- 用语义检索快速定位陌生代码入口。
- 把“先定位、再少量读取、再确认行号”的流程固化。
- 避免无边界地全仓 grep。

生效场景：

- 追踪后端接口调用链。
- 分析并发和状态机。
- 查找测试覆盖位置。

迭代优化：

- 优先使用 fast-context。
- fast-context 失败时切换 semble-search。
- 只在已知文件范围内使用 `rg` 做精确确认。

### MCP Server 与外部工具

常用配置方向：

- 代码语义检索：fast-context、semble-search。
- 官方文档检索：Context7 或智能搜索工具。
- 数据库调试：只读连接，限制写权限。
- 浏览器验证：使用独立浏览器上下文，避免污染个人会话。

解决的问题：

- 当前文档、框架 API 和线上行为可能变化，不能只依赖模型记忆。
- 多服务系统需要在浏览器、数据库和日志之间交叉验证。

迭代优化：

- 搜索外部技术文档时优先官方来源。
- 对数据库工具默认只读，需要写入时显式切换。
- 浏览器测试与真实个人浏览器隔离。

### IDE 插件和 Shell 辅助

常用项：

- GitHub Copilot：补全局部样板代码。
- Cursor 或 Windsurf：对中型模块做上下文问答。
- Codex CLI：在终端内执行跨文件修改、运行测试和整理补丁。
- Shell alias：封装常用命令，例如单测、类型检查、数据库迁移。

解决的问题：

- 减少重复命令输入。
- 将大模型用于分析和生成，将本地测试作为最终裁判。
- 保留命令输出，便于复盘。

迭代优化：

- 对生成代码强制本地运行测试。
- 对模型给出的路径和行号二次确认。
- 对涉及凭据的配置只提交示例，不提交真实密钥。

## 4.2 关键场景实录

### 场景一：追踪 Agent 崩溃后的任务状态

场景：任务一场景 A。

卡在哪里：最初不能确定 WebSocket 断开是否直接标记 runtime offline，也不能确定正在运行的 task 是否有超时兜底。

提示词：

```text
定位 Multica 中 daemon websocket connection、heartbeat/offline detection、task claiming、task status transitions 和 reconnect behavior 的实现。请返回入口函数、数据库查询、测试和关键文件路径，用于分析 daemon 崩溃后的 task 是否会泄漏。
```

AI 输出的价值：

- 快速定位 `server/internal/daemonws/hub.go`、`server/internal/handler/daemon.go`、`server/internal/service/task.go`、`server/cmd/server/runtime_sweeper.go`。
- 指出 WebSocket Hub 只维护连接，不直接写 runtime 状态。
- 提醒继续查看 `FailTasksForOfflineRuntimes` 和 `RecoverOrphanedTasksForRuntime`。

我的修正：

- 没有直接采用摘要结论，而是用 `nl -ba` 读取命中范围，确认具体行号。
- 补充 SQL 级证据，确认 stale runtime、offline task 和 stale task 三条清理路径。
- 区分“daemon 未重启”和“daemon 重启后 recover-orphans”两类恢复机制。

### 场景二：设计并验证任务编排引擎

场景：任务二核心实现。

卡在哪里：失败策略之间存在边界差异，尤其是 `retry` 超过次数后是否升级为 fail_fast，以及 `skip` 是否影响依赖它的后续任务。

提示词：

```text
为一个多 Agent DAG 任务编排引擎设计核心内存模型和测试。必须支持添加任务、添加依赖、检测环、根据依赖领取 ready task、限制并发，以及 fail_fast、retry、skip 三种失败策略。
```

AI 输出的价值：

- 帮助拆分出 Workflow 状态和 Task 状态。
- 提醒将并发限制放在 claim 阶段，而不是 ready 计算阶段。
- 提醒为循环依赖、菱形依赖、重试耗尽和跳过策略分别写测试。

我的修正：

- 选择 Python 标准库实现，避免交付代码依赖项目 monorepo 的包管理。
- 将 `skip` 定义为 `skipped` 终态，依赖它的下游任务也进入 `skipped`，不依赖它的任务继续运行。
- 将生产设计与内存实现分离：内存实现验证算法，设计文档说明数据库事务和行锁。
