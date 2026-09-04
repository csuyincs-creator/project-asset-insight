# project-asset-insight

> **项目资产解读器** — 给项目写一份“未来自己还能读懂，而且一眼能想起它长什么样”的快速重入指南。

## 简介

`project-asset-insight` 是一个 AI Agent Skill，用于对任意项目做长期知识资产解读，输出结构化 Markdown 笔记，并在项目存在可视界面时强制留下真实截图证据。

它重点回答：

- 这个项目到底是干什么的
- 它最核心的能力是什么
- 架构怎么组织
- 哪些模块值得借鉴或复用
- 以后什么时候应该重新打开它
- 只看哪些文件能快速重新理解
- 如果有 UI / Web / GUI / Demo，它真实运行后长什么样

默认不修改目标项目源码。

## v1.1.0 的核心变化

### 强制截图

只要项目存在任何可视界面，截图就是项目资产解读的强制证据。

Agent 必须实际尝试打开界面并生成截图。只有以下两种情况允许最终没有截图：

1. `NO_VISUAL_SURFACE`：确认整个项目没有 Web / GUI / Demo / Canvas / SVG / WebGL / 桌面界面等可视入口。
2. `CAPTURE_BLOCKED`：存在可视界面，但经过规定的运行和 fallback 尝试后，当前环境仍客观无法渲染。

“没装依赖”“第一次运行失败”“Agent 没浏览器”“Agent 不能看图”都不能单独成为跳过截图的理由。

### 截图与视觉理解解耦

Agent 不一定有视觉能力。

因此 Skill 将两件事分开：

- **截图生成**：只要有可视界面就必须完成。
- **截图语义复核**：Agent 有视觉能力时强制执行；没有视觉能力时标记 `VISION_UNAVAILABLE`。

无视觉能力不影响截图资产本身的生成和保存。

### 机器级截图配置

首次使用时需要向用户确认三个配置：

- `output_root`：Markdown 报告根目录
- `screenshot_root`：截图资产根目录
- `screenshot_scale`：截图倍率

配置保存在：

```text
%USERPROFILE%\.project-asset-insight\config.json
```

`screenshot_scale` 允许 `0.5`～`4.0`，常见选择为 `1 / 1.5 / 2 / 3`，但 Skill 不会替用户静默选择默认值。

`screenshot_root` 可以和 `output_root` 相同，也可以是独立素材目录，但必须由用户明确确认。

旧版配置如果只有 `output_root`，会触发一次配置迁移，只补问缺失的截图目录和 scale。

## 输出结构

报告：

```text
<output_root>/
└── <YYYY-MM>/
    └── <YYYY-MM-DD>-<项目>-<总结>-项目资产解读.md
```

截图资产：

```text
<screenshot_root>/
└── <YYYY-MM>/
    └── <YYYY-MM-DD>-<项目>-<总结>-项目资产解读.assets/
        ├── visual-evidence.json
        ├── 01-overview.png
        ├── 02-core-feature.png
        └── ...
```

如果项目只有一个主要页面，1 张截图即可；多页面项目通常保留 2～4 张，不为了数量硬凑。

## 工作流

```text
TODO-00  本机配置：报告目录 + 截图目录 + scale
    ↓
TODO-01  项目身份确认
    ↓
TODO-02  建立项目地图
    ↓
TODO-03  核心能力提炼
    ↓
TODO-04  核心架构理解
    ↓
TODO-05  借鉴价值分析
    ↓
TODO-06  可复用资产分类
    ↓
TODO-07  未来使用映射
    ↓
TODO-08  15 分钟阅读路线
    ↓
TODO-09  强制视觉运行、截图与校验
    ├── 09A 视觉界面探测
    ├── 09B 运行与截图
    ├── 09C 机器级校验
    └── 09D 视觉语义复核（能力存在时）
    ↓
TODO-10  报告生成 + 双 validator
```

## 视觉证据状态

### capture_status

- `CAPTURED`
- `NO_VISUAL_SURFACE`
- `CAPTURE_BLOCKED`

### review_status

- `VISION_REVIEWED`
- `VISION_UNAVAILABLE`

### verification_level

- `L0`：无截图，只适用于无可视界面或经证明的阻塞
- `L1`：截图文件成功生成并通过文件级检查
- `L2`：L1 + 浏览器 / DOM / Console / Network 等机器检查
- `L3`：完成截图视觉语义复核

`CAPTURED` 至少必须达到 `L1`。

## 安装

将本 Skill 放到支持 Skill / Plugin 的 AI Agent skills 目录即可。

目录结构：

```text
project-asset-insight/
├── SKILL.md
├── README.md
├── VERSION
├── references/
│   ├── workflow.md
│   ├── analysis-rules.md
│   ├── evidence-rules.md
│   ├── metadata-rules.md
│   ├── report-schema.md
│   └── visual-verification-rules.md
├── scripts/
│   ├── config_manager.py
│   ├── build_output_path.py
│   ├── build_visual_output_path.py
│   ├── capture_visual.py
│   ├── validate_visual_evidence.py
│   └── validate_report.py
└── templates/
    └── project-asset-report.md
```

核心 Python 脚本仅使用标准库。`capture_visual.py` 不要求 Python 浏览器库，而是调用本机已有 Chrome / Chromium / Edge 的 headless 截图能力作为兜底。

## 首次配置

Agent 必须先询问用户三个值，然后执行：

```bash
python scripts/config_manager.py set \
  "G:\\knowledge\\project-insight" \
  --screenshot-root "G:\\knowledge\\project-insight-assets" \
  --screenshot-scale 2
```

检查配置：

```bash
python scripts/config_manager.py status
```

读取完整配置：

```bash
python scripts/config_manager.py get
```

也可以读取单项：

```bash
python scripts/config_manager.py get --field screenshot_root
python scripts/config_manager.py get --field screenshot_scale
```

## 生成输出路径

报告：

```bash
python scripts/build_output_path.py \
  "<output_root>" "<project_name>" \
  --summary "<summary>" \
  --create-month-dir
```

截图资产目录：

```bash
python scripts/build_visual_output_path.py \
  "<screenshot_root>" "<project_name>" \
  --summary "<summary>" \
  --create
```

## 截图兜底

当 Agent 没有内置截图工具、但本机存在 Chrome / Chromium / Edge 时：

```bash
python scripts/capture_visual.py \
  --url "http://127.0.0.1:5173" \
  --output-dir "<视觉资产目录>" \
  --scale "<用户配置的 screenshot_scale>"
```

默认生成：

```text
01-overview.png
visual-evidence.json
```

也可指定：

```bash
python scripts/capture_visual.py \
  --url "http://127.0.0.1:5173/settings" \
  --output-dir "<视觉资产目录>" \
  --scale 2 \
  --name "02-settings.png"
```

## 报告结构

报告固定包含 12 个章节：

1. 30 秒看懂这个项目
2. 它解决什么问题
3. 核心能力
4. 核心架构与实现思路
5. 最值得借鉴的地方
6. 可复用资产
7. 可以进一步变成我的什么
8. 什么时候值得重新打开它
9. 15 分钟重新理解路线
10. 哪些地方不用继续浪费时间
11. **真实运行与视觉验证**
12. 最终资产结论

元信息新增：

- 截图资产目录
- 截图倍率
- 视觉验证状态

## Completion Gate

先验证视觉证据：

```bash
python scripts/validate_visual_evidence.py \
  "<visual-evidence.json>" \
  --screenshot-root "<screenshot_root>" \
  --report "<报告路径>"
```

再验证最终报告：

```bash
python scripts/validate_report.py \
  "<报告路径>" \
  --output-root "<output_root>" \
  --project-path "<当前项目绝对路径>" \
  --visual-evidence "<visual-evidence.json>"
```

只有两个命令都返回 exit code `0` 才算完成。

## 运行边界

为了截图，允许最小化运行项目；但仍然不允许把资产解读变成开发调试。

允许：

- 官方 dev / preview / demo
- 静态 HTML
- 已声明依赖的冻结安装
- 临时 venv
- headless 浏览器

禁止：

- 修改项目源码
- 修改 manifest / lockfile
- 升级依赖解决兼容问题
- 修 Bug
- 重构
- 真实支付、发布、发信、删除等生产副作用

详细规则见 `references/visual-verification-rules.md`。

## 适用于

可用于支持 Skill / Plugin 机制并能访问项目文件的 Agent，例如：

- Claude Code
- Cursor
- Continue.dev
- Cline
- Codex / 自定义 Agent

Agent 是否具备视觉理解能力不会影响截图资产的强制生成规则。

## 版本

当前版本：`v1.1.0`。

## License

MIT License
