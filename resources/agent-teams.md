# Agent Teams 参考资料

访问日期：2026-09-11。以下为网页核实与待读资料，不代表已运行产品或追踪源码。

| 资料 | 本轮用途 | 版本或证据边界 |
| --- | --- | --- |
| [Claude Code Agent Teams 官方文档](https://code.claude.com/docs/en/agent-teams) | 主产品公开机制 | 页面说明以 v2.1.178 后机制为基础，另含更新版本条目；实际安装版本未知 |
| [Anthropic：Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) | 区分预定义并行与动态任务分解 | 工程文章，不是证明特定产品实现的源码 |
| [LangChain TS Subagents](https://docs.langchain.com/oss/javascript/langchain/multi-agent/subagents) | 中心式委派的 TS 对照 | 文档已读取；源码提交尚未固定 |
| [AutoGen 论文](https://arxiv.org/abs/2308.08155) | 多 Agent 对话与协作控制的论文入口 | 本次仅查阅题录/摘要页，全文及具体版本研读待安排 |

## 已核实的少量起点

Claude 官方将团队描述为负责人、队友、共享任务列表和通信邮箱。队友各有上下文。页面仍标为实验功能；v2.1.178 前后的建立和清理方式不同，因此旧教程中的 TeamCreate/TeamDelete 不能直接套到当前文档。以上是公开说明，未作本机运行验证。[来源](https://code.claude.com/docs/en/agent-teams)

LangChain 的对照模式把子 Agent 包装成工具，由主 Agent 决定调用和汇总。它适合用来研究中心式委派，不等同于 Claude 的团队实现。[来源](https://docs.langchain.com/oss/javascript/langchain/multi-agent/subagents)

候选 Python 库 `langgraph-supervisor-py` 的 README 已建议多数场景直接通过工具实现 supervisor 模式，因此不将该库作为当前 TS 学习主线。[来源](https://github.com/langchain-ai/langgraph-supervisor-py)
