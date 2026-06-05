# Claude 本地授权配置摘要（已脱敏）

来源：`$HOME/.claude/settings.local.json`

该文件包含大量历史授权命令，原文含内网地址、一次性 root 密码、远程主机路径和代理配置片段，不能直接提交。此处保留真实配置类别和 MCP / tool 能力，删除具体敏感参数。

## 权限类别

- 浏览器自动化：`agent-browser` 的 open、snapshot、click、fill、press、screenshot、network、cookies、storage、tab、mouse、trace 等命令。
- GitHub 操作：`gh issue view`、`gh search issues`、`gh release view`、`gh api`、GitHub plugin MCP 的 issue、PR、code search、file contents 读取。
- 系统排查：`systemctl`、`journalctl`、`dmesg`、`coredumpctl`、`lsusb`、`v4l2-ctl`、`ip route`、`ip rule`、`getent hosts` 等。
- 包管理与构建：`pacman`、`paru`、`pnpm add/remove/update/info/list`、`npm view`、`cargo build --release`。
- 桌面环境：`niri`、`xwayland-satellite`、`kitty`、`yazi`、`sddm`、`hyprctl`。
- 远程维护：存在 `ssh`、`sshpass`、`scp` 历史授权；具体 IP、密码、主机和命令正文已删除。
- 代理与网络：存在 sing-box 相关历史授权；配置路径、控制密钥和内网地址已删除。

## MCP 工具

- `mcp__plugin_context7_context7__resolve-library-id`
- `mcp__plugin_context7_context7__query-docs`
- `mcp__plugin_github_github__search_issues`
- `mcp__plugin_github_github__search_code`
- `mcp__plugin_github_github__get_file_contents`
- `mcp__plugin_github_github__pull_request_read`
- `mcp__plugin_github_github__issue_read`
- `mcp__grok-search__web_search`
- `mcp__grok-search__web_fetch`
- `mcp__perplexity__search`

## 保留策略

- 本地授权文件不作为可复制配置提交。
- 可复制配置只保留工具类别、用途和 MCP 名称。
- 凡是出现内网地址、密码、token、cookie、代理 API 地址、私有主机路径的内容，全部用摘要替代。
