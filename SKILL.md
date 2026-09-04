# Project Asset Insight Skill

## Purpose

对“当前项目”做长期知识资产解读，并在项目存在可视界面时留下真实截图证据。

第一目标始终是：

理解项目
→ 提炼核心能力
→ 发现值得借鉴的设计
→ 识别可直接复用 / 改造复用 / 思路复用的资产
→ 建立未来重新打开项目的触发场景与阅读路线
→ 对可视项目完成真实运行、截图与校验
→ 输出 Obsidian 项目资产解读文档

## Core boundary

默认只读目标项目源码，不修改目标项目。

除 TODO-09 的最小化视觉验证外，不要主动：

- 安装依赖
- 启动项目
- 调试运行错误
- 修复 Bug
- 修改源码
- 重构项目
- 做 Git 审计
- 做测试覆盖分析
- 全量遍历并摘要所有文件

### Visual verification exception

为了确认项目真实视觉形态，TODO-09 允许并强制执行最小化运行、浏览器打开、截图与视觉证据校验。

允许：

- 使用项目已有运行环境
- 执行官方 dev / preview / demo 启动方式
- 打开静态 HTML
- 使用冻结依赖安装方式补齐项目已声明依赖
- 使用浏览器 headless 模式截图
- 使用 Skill 自带 `scripts/capture_visual.py` 作为截图兜底

仍然禁止：

- 修改目标项目源码
- 修改依赖声明或 lockfile
- 升级依赖以解决兼容性问题
- 为了截图而修 Bug 或重构
- 执行具有生产副作用的操作

原则：可以“为了看它长什么样而运行”，不能“为了让它跑起来而开发它”。

## Mandatory execution order

开始任务后，必须读取并遵守：

1. `references/workflow.md`
2. `references/analysis-rules.md`
3. `references/evidence-rules.md`
4. `references/metadata-rules.md`
5. `references/report-schema.md`
6. `references/visual-verification-rules.md`

必须严格执行 TODO-00 → TODO-10。

TODO-01～TODO-09 完成前，不得生成最终 Markdown。

## Machine-level config

机器级配置位置：

`%USERPROFILE%\.project-asset-insight\config.json`

完整配置必须包含：

- `output_root`
- `screenshot_root`
- `screenshot_scale`

### First run / migration

若配置不存在，TODO-00 必须向用户询问：

1. 这台机器统一把 Markdown 报告输出到哪里？
2. 这台机器统一把截图资产输出到哪里？
3. 截图使用多少 `screenshot_scale`？

`screenshot_scale` 允许 `0.5`～`4.0`。可以提示常见值 `1 / 1.5 / 2 / 3`，但不得替用户静默选择。

`screenshot_root` 可以和 `output_root` 相同，但必须由用户明确确认。

若旧配置只有 `output_root`，必须只补问缺失的 `screenshot_root` 与 `screenshot_scale`，然后迁移配置。

通过：

```bash
python scripts/config_manager.py set \
  "<output_root>" \
  --screenshot-root "<screenshot_root>" \
  --screenshot-scale "<scale>"
```

保存配置。

若配置完整且有效，后续直接读取，不得重复询问。

## Output paths

最终报告路径固定为：

`<output_root>/<YYYY-MM>/<YYYY-MM-DD>-<项目名称>-<一句话总结>-项目资产解读.md`

视觉资产目录固定为：

`<screenshot_root>/<YYYY-MM>/<YYYY-MM-DD>-<项目名称>-<一句话总结>-项目资产解读.assets/`

视觉资产目录至少包含：

- `visual-evidence.json`
- 若 `capture_status=CAPTURED`，至少一张截图，如 `01-overview.png`

## Mandatory screenshot rule

只要项目存在任何可视界面，截图就是强制证据，不是可选项。

Agent 必须：

1. 实际尝试打开可视界面。
2. 生成至少一张截图。
3. 生成或补全 `visual-evidence.json`。
4. 运行机器级视觉证据校验。
5. 若 Agent 有视觉理解能力，重新查看截图并完成语义复核。
6. 若 Agent 没有视觉理解能力，仍然保留截图与机器校验，并标记 `VISION_UNAVAILABLE`。

Agent 没有浏览器、没有截图工具、没有看图能力，都不能单独成为跳过截图的理由。

只允许三种最终 `capture_status`：

- `CAPTURED`
- `NO_VISUAL_SURFACE`
- `CAPTURE_BLOCKED`

其中：

- `NO_VISUAL_SURFACE` 必须证明整个项目不存在可视入口。
- `CAPTURE_BLOCKED` 必须留下真实运行尝试、错误与 fallback 检查记录。

## Completion gate

最终报告写入后，必须先执行：

```bash
python scripts/validate_visual_evidence.py \
  "<visual-evidence.json>" \
  --screenshot-root "<screenshot_root>" \
  --report "<报告路径>"
```

只有视觉证据验证 exit code 0 后，才能执行：

```bash
python scripts/validate_report.py \
  "<报告路径>" \
  --output-root "<output_root>" \
  --project-path "<当前项目绝对路径>" \
  --visual-evidence "<visual-evidence.json>"
```

两个 validator 都为 exit code 0 才算完成。

如果任一校验失败：修复报告或视觉证据后重新校验。
