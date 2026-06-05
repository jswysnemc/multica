# Plugins / MCP 配置快照（已脱敏）

## Claude 已启用插件

来源：`$HOME/.claude/settings.json` 与 `$HOME/.claude/plugins/installed_plugins.json`

- `code-review@claude-plugins-official`：代码审查流程。
- `commit-commands@claude-plugins-official`：提交命令辅助。
- `context7@claude-plugins-official`：官方文档和库文档检索。
- `document-skills@anthropic-agent-skills`：文档类 skill。
- `frontend-design@claude-plugins-official`：前端设计辅助。
- `github@claude-plugins-official`：GitHub issue、PR、代码搜索、文件读取。
- `rust-analyzer-lsp@claude-plugins-official`：Rust LSP。
- `clangd-lsp@claude-plugins-official`：C/C++ LSP。

## Codex 插件

来源：`$HOME/.codex/config.toml`

- `documents@openai-primary-runtime`：启用。
- `spreadsheets@openai-primary-runtime`：启用。
- `presentations@openai-primary-runtime`：启用。

## MCP 配置状态

Codex 侧 MCP 配置块当前大多为注释状态，保留作为可快速启用的模板：

- `grok-search`：stdio，命令为 `uvx --from git+https://github.com/GuDaStudio/GrokSearch grok-search`，API key 和代理 URL 已脱敏。
- `augment-context-engine`：stdio，命令为 `auggie --mcp --mcp-auto-workspace`，token 和 relay URL 已脱敏。
- `context7`：stdio，命令为 `npx -y @upstash/context7-mcp`。
- `perplexity`：HTTP MCP，URL 和 Authorization 已脱敏。
- `codegraph`：stdio，命令为 `codegraph serve --mcp`。

Claude 侧可用 MCP 工具来自已启用插件和本地授权：

- Context7：库 ID 解析和文档查询。
- GitHub：issue、PR、代码搜索和文件内容读取。
- Grok Search：网页搜索和网页抓取。
- Perplexity：搜索。

## 迭代原则

- 日常开发优先本地 semantic search，外部文档优先 Context7 和官方来源。
- GitHub MCP 用于 issue/PR/code 读取，写操作仍通过 `gh` 或浏览器确认。
- 搜索 MCP 涉及代理和 key，提交材料只保留结构，不保留可用凭据。
