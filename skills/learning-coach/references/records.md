# 仓库记录与进度规范

## 保存位置与命名

学习根目录放 `learning-hub.json`，内容为 `{"schema_version": 1, "language": "zh-CN"}`。已有其他组织方式时尽量映射，不擅自搬动文件；若要使用本 Skill 的进度脚本，采用下面的进度格式。

知识主题使用稳定的小写英文 ID，例如 `memory`、`agent-teams`；文件路径变化不改变 ID。日期用真实本地日期，事件文件名可加时间或递增后缀，避免同日覆盖。

按当前任务创建对应文件，不批量制造空档案：

| 资料 | 路径约定 | 模板 |
| --- | --- | --- |
| 主题 | `topics/<id>/overview.md` | `assets/topic.md` |
| 系统分析 | `systems/<id>/analysis.md` | `assets/system.md` |
| 论文 | `papers/<id>.md` | `assets/paper.md` |
| 计划 | `plans/<id>/plan.md` | `assets/plan.md` |
| 学习记录 | `sessions/<日期>-<主题>-<序号>.md` | `assets/session.md` |
| 测评 | `assessments/<日期>-<主题>-<序号>.md` | `assets/assessment.md` |
| 实验 | `experiments/<id>/report.md` | `assets/experiment.md` |
| 设计决策 | `decisions/<id>.md` | `assets/decision.md` |

模板中的“待填写”是作者需替换的字段，不是已完成内容。无数据时明确保留未知。`learner/` 保存用户实际提供的背景，`resources/` 保存出处；不从别的任务或私人文件擅自导入档案。

## 当前掌握状态

从 `assets/mastery.json` 初始化 `progress/mastery.json`。格式为：

```json
{
  "schema_version": 1,
  "topics": [
    {
      "id": "memory",
      "title": "记忆机制",
      "path": "topics/memory/overview.md",
      "prerequisites": [],
      "dimensions": {
        "概念理解": {"status": "未评估", "evidence": []},
        "源码追踪": {"status": "未评估", "evidence": []},
        "设计判断": {"status": "未评估", "evidence": []},
        "独立实现": {"status": "未评估", "evidence": []},
        "效果验证": {"status": "未评估", "evidence": []}
      },
      "weak_points": [],
      "next_action": "明确本轮需要解决的记忆问题",
      "review_on": null,
      "updated_on": "2026-09-11"
    }
  ]
}
```

上面是格式示例，不要原样记录为用户已经开始学习。主题 `path` 指向已存在的文件，前置 ID 必须存在且无环。未开始的任务在计划中记录，不需要先添加大量主题状态。

每条证据用对象：`{"path":"assessments/实际文件.md","summary":"对应真实表现与验收条件的简述","assistance":"独立完成"}`。`path` 必须是仓库内已存在的文件，原始材料里保存引用 URL 或代码链接。辅助程度取值：独立完成、提示下完成、共同完成、Agent生成、自述。

已验证维度需有非“自述”、非“Agent生成”的证据；独立实现还必须有“独立完成”证据。脚本仅检查这些结构约束，Agent 仍须阅读证据判断是否充分。`updated_on` 与 `review_on` 为真实日期 `YYYY-MM-DD`，无复习安排用 null。

## 更新顺序

1. 读取现有记录，避免覆盖其他主题或近期工作。
2. 保存本次学习或测评事件，保留用户实际作答、辅助情况、判断依据和日期。更正历史用补充说明，不能把错误答案改成正确答案。
3. 只更新本次证据涉及的维度、薄弱点、下一步及日期。用户说“学完了”可以完成任务，不能自动提升全部维度。
4. 计划变化保留原因；历史事件是依据，`mastery.json` 是当前摘要，`dashboard.md` 是生成视图，不分别手动维护多份统计。
5. 用 `scripts/progress.py --root <学习根目录>` 校验；加 `--write-dashboard` 在通过后写 `progress/dashboard.md`。不做未经授权的提交、推送或后台提醒。

多个 Agent 同时工作时分配不同事件文件，更新共享进度前重读。遇到冲突核对两份证据后合并，不以较新的文件直接覆盖另一份。
