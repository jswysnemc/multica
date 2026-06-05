# 全栈研发工程师综合笔试解答总览

## 交付目录

```text
submission/
├── README.md
├── task1/
│   ├── setup-log.md
│   └── fault-analysis.md
├── task2/
│   ├── design-doc.md
│   └── src/
│       ├── README.md
│       ├── test_workflow_engine.py
│       └── workflow_engine.py
├── task3/
│   ├── fix-report.md
│   └── pr-link.txt
├── task4/
│   ├── ai-configs/
│   │   ├── CLAUDE.example.md
│   │   ├── codex-config.example.toml
│   │   └── code-search-skill.example.md
│   └── ai-usage.md
└── fork-repo-link.txt
```

## 验证命令

任务二核心实现使用 Python 标准库，不依赖第三方包。

```bash
python3 -m unittest discover -s submission/task2/src -p 'test_*.py'
```

## 说明

任务一的搭建记录复用了本仓库已有的 `DEPLOYMENT_NOTES.md` 和运行截图。任务一故障分析基于当前仓库源码追踪，重点覆盖 Agent 崩溃、并发领取和 WebSocket 重连三个场景。
