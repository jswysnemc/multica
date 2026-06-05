# 任务四：AI 工作流

## 4.1 AI 编程工具配置

### 脱敏说明

本节提交真实配置的脱敏快照，不提交可直接复用的密钥或私有环境。

脱敏规则：

- `$HOME` 替代真实用户主目录。
- `<redacted>` 替代 token、API key、cookie、密码、Authorization header。
- `<redacted-api-proxy>` 替代私有模型代理地址。
- `<private-ip>` 替代内网地址。
- 历史授权命令中涉及远程主机、代理配置、一次性密码、私有路径的内容只保留类别摘要。
- 不提交 `auth.json`、`.credentials.json`、history、sqlite 日志、会话缓存和浏览器 cookie。

### 实际提交的配置文件

- `task4/ai-configs/CLAUDE.redacted.md`：全局开发指令，来自 `$HOME/.claude/CLAUDE.md`。
- `task4/ai-configs/codex-instructions.redacted.md`：Codex 短全局指令，来自 `$HOME/.codex/instructions.md`。
- `task4/ai-configs/codex-config.redacted.toml`：Codex 真实配置快照，来自 `$HOME/.codex/config.toml`。
- `task4/ai-configs/claude-settings.redacted.json`：Claude settings 真实结构快照，来自 `$HOME/.claude/settings.json`。
- `task4/ai-configs/claude-settings-local.summary.md`：Claude 本地授权摘要，来自 `$HOME/.claude/settings.local.json`。
- `task4/ai-configs/skills-inventory.redacted.md`：真实安装的 skills 清单，来自 `$HOME/.claude/skills`。
- `task4/ai-configs/plugins-and-mcp.redacted.md`：Plugins 与 MCP 配置摘要，来自 Claude / Codex 本地配置。

### 全局指令

解决的问题：

- 统一输出风格，避免 AI 署名、Emoji、模板化结尾和不自然中文。
- 把“正确、清晰、严谨”作为默认质量门槛，减少低质量抽象。
- 固化检索优先级：未知代码位置先用 `fast-context`，失败后用 `semble-search`，`rg` 只做精确确认。

生效场景：

- 阅读陌生代码库前，先确认项目指令与全局指令是否冲突。
- 写提交信息、PR 描述、中文文档时应用隐私和表达规范。
- 需要全仓理解时，通过语义检索定位入口，再读取少量目标文件。

迭代优化：

- 把“禁止 AI 署名”和“UI 禁用 Emoji”放入全局规则，避免每个项目重复声明。
- 把代码检索工具顺序写成硬规则，减少无边界全仓搜索。
- 把中文风格约束写成自检项，降低交付文档的口语化和翻译腔。

### Codex 配置

真实配置摘要：

- 模型提供方：`OpenAI`。
- 默认模型：`gpt-5.5`。
- 推理强度：`xhigh`。
- 上下文窗口：`272000`。
- 响应存储：`disable_response_storage = true`。
- 网络：`network_access = "enabled"`。
- 审批策略：`approval_policy = "never"`。
- 沙箱：`sandbox_mode = "danger-full-access"`。
- 状态栏：模型、上下文剩余、Git 分支、当前目录。
- 插件：`documents`、`spreadsheets`、`presentations` 启用。
- 当前仓库：`$HOME/workspace/writeen_exam/test1/multica` 标记为 trusted。

解决的问题：

- 适合长上下文代码审查和跨文件修改。
- 本地工作流默认允许执行命令和网络访问，但通过人工规则约束破坏性操作。
- 启用文档、表格、演示插件，用于多格式交付。

生效场景：

- 多文件代码修改。
- 本地测试和构建验证。
- 文档、表格、演示等交付物生成。

迭代优化：

- 关闭响应存储，降低隐私风险。
- trusted project 只作为本地执行白名单，不提交完整私有路径清单。
- MCP 配置保留为注释模板，启用前先确认密钥和代理地址。

### Claude 配置

真实配置摘要：

- 语言：中文。
- 模型环境：`ANTHROPIC_MODEL = "opus[1m]"`，其他默认模型映射见 `claude-settings.redacted.json`。
- 非必要流量禁用：`CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC = "1"`。
- Tool Search：`ENABLE_TOOL_SEARCH = "true"`。
- 权限模式：`acceptEdits` / `bypassPermissions`。
- 额外可访问目录：`$HOME/.local/bin`、`/tmp`、若干本地配置目录。
- PreToolUse hook：对 `Grep|Glob` 注入检索规范提醒。
- 状态栏：本地 `ccline` 脚本。

解决的问题：

- 让模型在错误使用 grep/glob 前收到检索策略提醒。
- 将中文输出、插件、状态栏和权限模式固定到全局。
- 允许本地 CLI 与 MCP 工具协同工作。

生效场景：

- 代码库考古。
- GitHub issue / PR 阅读。
- 官方文档检索。
- 浏览器自动化和本地桌面验证。

迭代优化：

- 将历史授权命令放入 `settings.local.json`，交付时只提交摘要，不提交敏感命令正文。
- 通过 hook 纠正工具选择，而不是只依赖提示词记忆。
- 保留插件启用状态，减少每个项目重复配置。

### Skills

真实安装分类：

- 代码检索：`fast-context`、`semble-search`、`ace-codebase-search`、`code-search-tools-bundle`。
- 网络搜索：`smart-search-cli`、`anysearch`、`zhihu-search`。
- 浏览器和桌面自动化：`agent-browser`、`niri-use`。
- 图像与图表：`gpt2api-image`、`drawio`、`mmdc-diagram-png`、`remotion-best-practices`、`ui-ux-pro-max`。
- 垂直业务：`boss-agent-cli`、`snemc-blog-agent`、`tutor`。

解决的问题：

- 代码检索 skill 解决陌生代码库定位问题。
- 搜索 skill 解决外部资料时效性问题。
- 浏览器和桌面 skill 解决 UI 验证、截图和真实交互问题。
- 图表和文档 skill 支持交付材料生成。

迭代优化：

- 语义检索优先，精确 grep 后置。
- 技术文档优先 Context7 或官方来源，娱乐性搜索才用 anysearch。
- 图表类需求优先 drawio 或 Mermaid，不混用 raster 图像生成。

### Plugins 与 MCP

真实启用插件：

- Claude：`code-review`、`commit-commands`、`context7`、`document-skills`、`frontend-design`、`github`、`rust-analyzer-lsp`、`clangd-lsp`。
- Codex：`documents`、`spreadsheets`、`presentations`。
- MCP 工具：Context7、GitHub、Grok Search、Perplexity；Codex 侧还有 grok-search、augment-context-engine、context7、perplexity、codegraph 的注释模板。

解决的问题：

- GitHub 插件用于 issue、PR、代码搜索和文件读取。
- Context7 用于官方文档检索，避免依赖模型旧记忆。
- LSP 插件用于语言级语义信息。
- Codex 插件用于文档、表格、演示等非代码交付。

迭代优化：

- GitHub 写操作仍优先通过 `gh` 完成，便于保留命令记录。
- 搜索类 MCP 的代理 URL 和密钥不进入交付物。
- 本地授权命令只提交分类摘要，避免暴露内网环境。

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
