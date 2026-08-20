# project-asset-insight

> **项目资产解读器** — 给项目写一份「未来自己还能读懂的」快速重入指南。

## 简介

你电脑里攒了一堆项目源码（GitHub clone、下载的 zip、别人的项目），时间一长：

- 忘记这个项目是干什么的
- 想起来某个功能但不知道在哪个文件
- 想复用某个模块但不知道从哪下手

本项目是一个 **AI Agent Skill**，用于对任意项目做长期知识资产解读，输出一份结构化的 Markdown 笔记，可存入 Obsidian / Notion / Typora 等知识管理工具长期保存。

**关键原则：只读不运行。** 不安装依赖，不启动项目，不修 bug，不重构，只做「理解 + 提炼 + 记录」。

## 功能特性

| 能力 | 说明 |
|---|---|
| 项目身份识别 | 读 README / package.json / Git remote / 目录名，一句话说清项目是什么 |
| 项目地图构建 | 识别入口、核心模块、UI、API、数据层、插件，不逐文件审计 |
| 核心能力提炼 | 3-10 个能力点，每个绑定**证据路径** |
| 架构理解 | 解释分层原因、调用链、扩展点 |
| 借鉴价值分析 | 从架构 / 模块 / API / Prompt / Agent / UI 等维度检查 |
| 可复用资产分类 | A 直接复用 / B 改造复用 / C 思路复用 |
| 未来使用映射 | 问题 → 能力/模块映射，需要时知道回来看哪 |
| 15 分钟阅读路线 | 5-10 个关键文件 + 看什么，快速重新理解 |
| 避坑指南 | 指出样板代码、自动生成内容、低价值模块 |
| 输出校验 | 自动检查元信息 / 章节 / 占位符 / 文件名 / 证据路径 |

## 安装

将本 Skill 放到你的 AI Agent 的 skills 目录即可，Agent 会自动识别 `SKILL.md` 作为入口。

**目录结构：**

```
project-asset-insight/
├── SKILL.md                  # Skill 主入口
├── README.md                 # 本文件
├── VERSION                   # 语义版本号
├── references/               # 执行规则
│   ├── workflow.md           # TODO-00 → TODO-09 状态机
│   ├── analysis-rules.md     # 分析规则
│   ├── evidence-rules.md     # 证据绑定与推断规则
│   ├── metadata-rules.md     # 元信息填写规则
│   └── report-schema.md      # 报告结构规范
├── scripts/                  # 辅助脚本
│   ├── config_manager.py     # 机器级配置管理（output_root）
│   ├── build_output_path.py  # 输出路径生成器
│   └── validate_report.py    # 最终报告校验器
└── templates/
    └── project-asset-report.md  # 报告模板
```

Python 脚本仅使用标准库（`argparse` / `json` / `os` / `re` / `pathlib` / `socket` / `datetime`），无需 `pip install`。

## 使用方式

### 首次使用（TODO-00）

首次运行时，Skill 会询问「这台机器统一输出到哪里」。你只需要回答一个目录路径，例如：

```
G:\YINCS 知识库\10 输入与素材\01 项目资产解读
```

配置会保存在用户主目录下的 `.project-asset-insight/config.json`，后续自动沿用，不再询问。

手动设置配置：

```bash
python scripts/config_manager.py set "G:\YINCS 知识库\10 输入与素材\01 项目资产解读"
```

### 日常使用（TODO-01 → TODO-09）

在 AI Agent 中打开目标项目目录，然后触发 Skill：

```
请对当前项目做资产解读
```

或：

```
Analyze this project and generate an asset insight report
```

**自动执行流程：**

```
TODO-00  读取本机配置（或询问 output_root）
    ↓
TODO-01  项目身份确认（谁、从哪来、解决什么）
    ↓
TODO-02  建立项目地图（骨架理解，不逐文件审计）
    ↓
TODO-03  核心能力提炼（3-10 个，带证据路径）
    ↓
TODO-04  核心架构理解（为什么这么分层）
    ↓
TODO-05  借鉴价值分析（哪些设计值得学）
    ↓
TODO-06  可复用资产分类（A/B/C 三类表格）
    ↓
TODO-07  未来使用映射（问题 → 模块）
    ↓
TODO-08  关键阅读路线（15 分钟重入）
    ↓
TODO-09  报告生成 + 校验
```

### 输出路径

固定为：

```
<output_root>/<YYYY-MM>/<YYYY-MM-DD>-<项目名称>-<一句话总结>-项目资产解读.md
```

例如：

```
G:\YINCS 知识库\10 输入与素材\01 项目资产解读\2026-08\2026-08-20-dsh-oil-creator-数据可视化工具-项目资产解读.md
```

- 日期为当天日期
- 一句话总结由 AI 自动提炼（限 30 字）
- **月份目录不存在时自动创建**

## 输出报告结构

| 章节 | 内容 |
|---|---|
| 元信息表 | 来源、主机、时间、版本、项目地址、类型、接触程度、标签 |
| 01｜30 秒看懂 | 它是什么、干什么、核心价值、为什么值得知道（100-300 字） |
| 02｜解决什么 | 使用背景、原始问题、项目带来的价值 |
| 03｜核心能力 | 3-10 个能力点，每个绑定证据路径 |
| 04｜核心架构 | 调用链、分层与扩展点 |
| 05｜值得借鉴 | 真正值得学习的设计（不足 3 项不硬凑） |
| 06｜可复用资产 | A 直接复用 / B 改造复用 / C 思路复用（表格） |
| 07｜变成我的 | Skill / Agent / MCP / 工具 / 脚本 / UI 等 |
| 08｜重新打开 | 未来问题 → 对应能力/模块 |
| 09｜15 分钟路线 | 5-10 个关键文件 + 看什么 |
| 10｜绕过这里 | 样板代码、第三方代码、低价值模块 |
| 11｜最终结论 | 核心价值 / 最值得借鉴 / 是否值得深入研究 |

## 校验机制

每份报告写入后，必须通过 `validate_report.py` 校验：

```bash
python scripts/validate_report.py \
  "<报告路径>" \
  --output-root "<output_root>" \
  --project-path "<当前项目绝对路径>"
```

**校验项：**

- 报告文件存在且长度 ≥ 1000 字符
- 11 个元信息字段完整填写（无空值、无占位符）
- 11 个必要章节全部存在
- 无残留占位符（`待填写` / `TBD` / `TODO` / `xxx` / `<实际值>` 等）
- 报告中包含至少一处证据路径（`xxx/xxx.xxx` 格式）
- 文件名匹配 `YYYY-MM-DD-项目-总结-项目资产解读.md`
- 父目录格式为 `YYYY-MM`
- 报告位于 output_root 目录下

**校验结果：**

- Exit code `0` → 通过
- Exit code `1` → 失败，需修复后重试

## 漂移阻断（Don'ts）

本 Skill 明确禁止以下行为，防止 AI 跑偏：

- ❌ 安装依赖（`npm install` / `pip install` 等）
- ❌ 启动项目（`npm run` / `python main.py` 等）
- ❌ 调试运行错误
- ❌ 修复 Bug
- ❌ 修改源码
- ❌ 重构项目
- ❌ 做 Git 审计
- ❌ 做测试覆盖分析
- ❌ 全量遍历并摘要所有文件

发现运行、构建、测试信息时，只能作为辅助事实，不得让报告围绕这些内容展开。

## 辅助脚本

### `scripts/config_manager.py`

管理本机配置（`~/.project-asset-insight/config.json`）。

```bash
python scripts/config_manager.py set "G:\output"   # 设置 output_root
python scripts/config_manager.py get               # 读取 output_root
python scripts/config_manager.py status            # 查看完整配置
```

### `scripts/build_output_path.py`

生成最终报告输出路径，自动创建月份目录。

```bash
python scripts/build_output_path.py "G:\output" "my-project" --summary "数据可视化工具" --create-month-dir
# 输出: G:\output\2026-08\2026-08-20-my-project-数据可视化工具-项目资产解读.md
```

参数：
- `output_root`：必填，输出根目录
- `project_name`：必填，项目名称
- `--summary`：可选，AI 生成的一句话总结（限 30 字）
- `--create-month-dir`：自动创建月份目录
- `--date`：可选，指定日期（默认今天）

### `scripts/validate_report.py`

校验最终报告是否符合规范。

```bash
python scripts/validate_report.py "G:\output\2026-08\my-project-数据可视化工具-项目资产解读.md" \
  --output-root "G:\output" \
  --project-path "C:\projects\my-project"
```

## 适用于

本 Skill 兼容任何支持 Skill/Plugin 机制的 AI Agent，例如：

- **Claude Code**
- **Cursor**
- **Continue.dev**
- **Cline**
- **自定义 Agent**

只要 Agent 能加载 `SKILL.md` 并执行 Python 脚本，即可使用本项目。

## 版本

当前版本：`v1.0.0`（见 `VERSION` 文件）

## 许可

MIT License

## 仓库

[project-asset-insight](https://github.com/csuyincs-creator/project-asset-insight)
