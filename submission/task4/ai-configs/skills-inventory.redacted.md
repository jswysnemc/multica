# Skills 清单（真实安装，已脱敏）

来源：`$HOME/.claude/skills`

脱敏规则：

- 不包含 skill 脚本中的凭据、缓存、历史输出。
- 保留真实 skill 名称和用途。
- 私有路径统一写为 `$HOME`。

## 代码检索类

- `fast-context`：语义代码库上下文检索。用于不知道文件位置、需要按自然语言定位实现、追踪调用链和收集定义。
- `semble-search`：本地 Semble CLI 语义检索。用于 fast-context 失败或需要另一套检索结果时。
- `ace-codebase-search`：通过 ace-tool-rs 做语义代码检索。
- `code-search-tools-bundle`：同一套代码检索工具的 bundle，包含 `fast-context`、`semble-search`、`ace-codebase-search`。

## 网络与资料搜索类

- `smart-search-cli`：CLI-first 网络研究、官方文档检索、URL 内容提取。
- `anysearch`：实时搜索、垂直域搜索、批量搜索和 URL 抽取。
- `zhihu-search`：知乎站内内容搜索。

## 浏览器和桌面自动化

- `agent-browser`：浏览器自动化、页面测试、截图、PDF、已登录会话工作流。
- `niri-use`：niri Wayland 桌面观察和操作。默认优先使用隔离 nested niri 会话。

## 图像、图表、演示

- `gpt2api-image`：通过 gpt2api 图像端点生成 raster 图片。
- `drawio`：生成 draw.io 图、流程图、架构图、ER 图、序列图。
- `mmdc-diagram-png`：生成 Mermaid 图并导出 PNG。
- `remotion-best-practices`：Remotion 视频生成最佳实践。
- `ui-ux-pro-max`：UI/UX 设计与审查，包含风格、配色、字体、图表、前端栈建议。

## 垂直业务类

- `boss-agent-cli`：BOSS 直聘职位搜索、筛选、打招呼、投递和流水线管理。
- `snemc-blog-agent`：通过公开 agent API 读取或操作博客内容。
- `tutor`：数学题讲解、HTML 可视化、TTS 和 Manim 动画生成。

## 本次笔试实际使用

- `fast-context`：定位 daemon heartbeat、runtime sweeper、任务领取和 WebSocket 重连路径。
- `smart-search-cli`：用于技术文档和官方资料优先检索的日常配置，本次主要依赖本地源码。
- `drawio` / `mmdc-diagram-png`：作为图表输出备选，本次文档直接使用 Mermaid 文本图。
