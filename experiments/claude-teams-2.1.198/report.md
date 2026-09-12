# Claude Code 2.1.198：一次真实的团队执行

日期：2026-09-12。执行状态：已运行并退出。实验由学习助手操作，不作为学习者独立实现或已掌握的证据。

## 环境与边界

- 本机 `claude --version` 返回 2.1.198。
- 使用用户现有模型配置；启动界面显示 glm-5.2。负责人实际创建队友时传入 `model: sonnet`，因此不能声称队友一定使用与负责人相同的后端模型；本次未抓取请求核实别名映射。
- 单次启动设置 `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`，选择 `in-process`，保留 default 权限模式。
- 使用 `--safe-mode` 排除用户自定义 hooks、插件、MCP 等对实验的影响，保留现有认证与模型选择；结果代表该启动条件，不覆盖所有用户定制行为。
- 仅一个负责人、一个 observer 队友；读取自建 `workspace/brief.md`，不执行项目代码。

官方文档是不断更新的，本机版本低于页面中的部分版本条目。本文用运行证据限定结论。[官方文档](https://code.claude.com/docs/en/agent-teams)

## 实际工具顺序

从本次主会话和队友转录中提取了工具调用与结果，未保存模型思考或完整会话。参见 [工具事件](tool-events.json)。以下时间为 UTC，显示为北京时间需加 8 小时。

| 时间 | 执行者 | 工具及结果 |
| --- | --- | --- |
| 03:15:30 | 负责人 | TaskCreate：创建任务 #1 |
| 03:15:35 | 负责人 | TaskUpdate：把 owner 设为 observer |
| 03:15:39 | 负责人 | Agent：传入 name=observer、subagent_type=general-purpose，成功启动命名队友 |
| 03:15:41 | observer | Read：读取 brief.md 中的 TEAM-LAB-198 |
| 03:15:43.319 | observer | SendMessage：向 main 发送标记 |
| 03:15:43.322 | 运行时 | 返回 success=true，消息已排入主会话下一轮 |
| 03:15:43.410 | observer | TaskUpdate：把任务 #1 设为 completed |
| 03:15:46 | 负责人 | TaskGet：读取到任务 #1 为 completed |

负责人收到标记，界面随后显示 observer 空闲。第二轮只创建一个名为 storage-probe 的 pending 任务，以便读取其文件，不再新增队友。

这次消息发送与状态完成是两次独立工具调用。它们在本次记录中先后发生，不能据此证明系统为二者提供了原子事务或 exactly-once 保证。

## 本地存储实测

限定检查本次实验工作目录匹配的团队，采样内容见 [状态快照](observed-state.json)。

```text
~/.claude/teams/<本次团队>/
├── config.json
└── inboxes/
    ├── observer.json
    └── team-lead.json

~/.claude/tasks/<本次团队>/
├── .lock
├── .highwatermark
└── 2.json
```

配置中实际存在 team-lead 和 observer，backendType 均为 in-process。这里证明的是运行时记录的后端模式，不把逻辑 Agent 直接等同于独立操作系统进程。

第二个任务文件的实际内容：

```json
{
  "id": "2",
  "subject": "storage-probe",
  "description": "保持 pending 供外部读取任务文件。不分配、不执行、不完成。",
  "status": "pending",
  "blocks": [],
  "blockedBy": []
}
```

注意任务依赖字段实际为 `blocks` 和 `blockedBy`，不是先前 TS 教学模型的 `dependsOn`。本次未设置依赖或竞争领取，也未采集到 in_progress 的中间态。

官方说明领取使用文件锁；本机也观察到 `.lock`，但单凭这个文件还不能证明锁的具体算法、作用域和崩溃恢复语义。本次没有实施竞争测试或追踪锁的实现源码。[官方说明：Assign and claim tasks](https://code.claude.com/docs/en/agent-teams#assign-and-claim-tasks)

采样时两个 inbox 文件均为空列表，因此本次确认了邮箱文件存在和真实发送工具结果，没有捕获到消息留在文件中的瞬间。任务 #1 的 completed 状态由 TaskGet 结果证实；采样时其 JSON 已不在目录，原因未验证，不能笼统宣称所有完成任务都会永久保留。

## 生命周期观察

使用 `/exit` 后，界面提示仍有队友，选择退出并停止后台工作。进程正常退出后：

- 本次团队目录不再存在。
- 本次任务目录仍存在。
- pending 的 `2.json` 仍存在。

没有发送 shutdown_request，本次不证明优雅关闭协议的具体行为。测试会话已停止，没有留在后台继续运行。待办探针文件保留，便于之后复查。

## 与前面理论课的关系

| 先前讨论 | 现在能针对 Claude Code 说什么 |
| --- | --- |
| 可以用数据库条件更新领取任务 | 这是我们的设计选项；Claude 官方说明为文件锁，本机看到文件存储与锁文件 |
| 用任务表管理状态 | 本版实测任务以本地 JSON 表达；工具负责创建、更新与读取 |
| 队友通过消息协调 | 本次实测 SendMessage 排入主会话下一轮；与任务状态更新分开 |
| 超时、心跳、租约 | 仍属于通用设计；本实验没有证明 Claude 使用了这些机制 |
| 完成前自动验收结果 | 本次只观察到队友调用 TaskUpdate，并未证明运行时对任意结果自动验收 |

## 复现实验

在只包含实验文件的目录中启动交互式会话（不能用 `-p` 替代团队实测）：

```bash
CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 claude --safe-mode --permission-mode default --teammate-mode in-process
```

输入：“创建一个名为 observer 的队友，建立一个读取 brief.md 并回报标记的任务。让队友读取文件，用 SendMessage 回报，再完成任务。不要创建更多队友或执行代码。最后等待我检查。”

具体模型选择与费用取决于现有配置。本次未导出密钥、服务地址或其他会话内容。若要严格比较模型，后续需核实负责人和队友各自的真实模型映射。

## 下一步

让学习者沿上述工具事件解释三个变化：任务 owner、消息投递、任务 completed。然后做一次固定版本的任务依赖实验，再按证据选择是否追踪源码或构造 TS 对照；不先假设运行时采用数据库、租约或特定消息协议。
