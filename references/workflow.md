# 强制工作流｜TODO 状态机

本 Skill 使用 11 个阶段，禁止跳步。

## TODO-00｜本机配置检查

目标：确认本机统一输出目录与截图配置。

检查 `%USERPROFILE%\.project-asset-insight\config.json`。

必须得到三个机器级字段：

- `output_root`：Markdown 报告输出根目录
- `screenshot_root`：截图资产输出根目录
- `screenshot_scale`：截图缩放倍率，允许 `0.5`～`4.0`

规则：

- 若配置不存在：一次性询问用户这三个字段。
- 若旧配置仅有 `output_root`：只询问缺失的 `screenshot_root` 与 `screenshot_scale`。
- `screenshot_root` 可以与 `output_root` 相同，但必须由用户明确选择，不得静默默认。
- `screenshot_scale` 常见值可提示 `1 / 1.5 / 2 / 3`，但不得替用户选择。
- 校验路径格式与 scale 范围。
- 必要时创建目录。
- 保存 config.json。
- 若配置存在且完整有效：直接读取，不得重复询问。
- 若任一路径失效或 scale 非法：要求用户重新指定，不得自动替换。

完成条件：得到有效的 `output_root`、`screenshot_root`、`screenshot_scale`。

## TODO-01｜项目身份确认

只回答：项目是谁、来自哪里、解决什么问题。

优先读取：
- 当前目录名
- README / README_CN
- package.json / pyproject.toml / Cargo.toml / go.mod / pom.xml
- Git remote
- homepage / docs 首页

输出中间结论：项目名称、项目路径、来源、项目网址、一句话定位、可信度。

禁止在此阶段深挖源码。

## TODO-02｜建立项目地图

目标：理解项目骨架，而不是逐文件审计。

识别：
- 入口
- 核心模块
- UI
- API
- 数据层
- Adapter / Plugin / Agent / Prompt / Script
- Examples / Docs

形成简洁项目地图与数据/调用流。

同时记录是否发现任何潜在可视界面入口，供 TODO-09 使用。

## TODO-03｜核心能力提炼

提炼 3～10 个真正核心能力；不足 3 个时不要硬凑。

每个能力必须包含：
- 能力是什么
- 为什么重要
- 大概怎么实现
- 证据路径
- 可信度

## TODO-04｜核心架构理解

解释模块为什么这样组合：
- 核心层
- 胶水层
- 扩展层
- 数据流
- 抽象边界

重点回答：哪些架构设计值得借鉴，哪些只是普通工程实现。

## TODO-05｜借鉴价值分析

从架构、模块划分、数据 Schema、API、Agent、Prompt、Skill、插件、Adapter、Session、浏览器控制、UI、自动化、配置、缓存、日志、异常处理、工程组织等方向检查。

每项明确回答：以后做什么时能用上这个思路。

## TODO-06｜可复用资产分类

强制分三类：

A. 可直接复用
B. 适合改造后复用
C. 只借鉴设计思路

每个资产写清：
- 是什么
- 在哪里
- 为什么有价值
- 怎么复用
- 复用成本
- 耦合程度

禁止硬凑分类。

## TODO-07｜未来使用映射

形成“问题 → 项目能力/模块”的映射。

例如：
- 以后想做多平台采集 → 看 Adapter
- 以后想复用登录态 → 看 Session/CDP

目标：让未来的自己知道什么时候重新想到这个项目。

## TODO-08｜关键阅读路线

生成“15 分钟重新理解路线”，按顺序列出 5～10 个关键文件/目录。

每项写：
- 为什么看
- 重点看什么
- 看完能理解什么

## TODO-09｜强制视觉运行、截图与校验

必须读取并遵守 `references/visual-verification-rules.md`。

### TODO-09A｜视觉界面探测

判断项目是否存在 Web / GUI / Demo / Canvas / SVG / WebGL / Electron / Tauri / Flutter / Qt / Gradio / Streamlit 等可视界面。

只允许三种最终截图状态：

- `CAPTURED`
- `NO_VISUAL_SURFACE`
- `CAPTURE_BLOCKED`

### TODO-09B｜强制运行与截图

只要存在任何可视界面，就必须尝试打开并生成截图。

截图资产目录通过：

```bash
python scripts/build_visual_output_path.py \
  "<screenshot_root>" "<项目名称>" \
  --summary "<一句话总结>" \
  --create
```

截图必须使用 TODO-00 中用户确认的 `screenshot_scale`。

若 Agent 没有内置截图能力，优先使用已有浏览器自动化；仍不可用时可调用：

```bash
python scripts/capture_visual.py \
  --url "<页面 URL 或 file:// 地址>" \
  --output-dir "<视觉资产目录>" \
  --scale "<screenshot_scale>"
```

截图成功时至少生成一张 `01-overview.png`。

### TODO-09C｜机器级校验

生成或补全 `visual-evidence.json`，记录截图状态、截图列表、scale、viewport、运行信息等。

机器级校验必须把 manifest 中的 `screenshot_scale` 与 TODO-00 机器配置里的 `screenshot_scale` 逐值核对，禁止 Agent 临时改倍率。

### TODO-09D｜视觉语义复核

- Agent 有视觉能力：必须重新查看截图并做视觉检查，`review_status=VISION_REVIEWED`。
- Agent 无视觉能力：继续保留截图与机器校验，`review_status=VISION_UNAVAILABLE`，不得假装看过图片。

### 无截图例外

只有以下情况允许最终没有截图：

1. `NO_VISUAL_SURFACE`：确认项目完全不存在可视界面，并记录检查入口与证据。
2. `CAPTURE_BLOCKED`：确认存在可视界面，但完成规定的运行与回退尝试后仍客观无法渲染，并记录实际尝试、错误与 fallback。

“没装依赖”“第一次运行失败”“Agent 没浏览器”“Agent 不能看图”都不能单独作为跳过截图的理由。

## TODO-10｜报告生成与全量验证

只有 TODO-01～09 全部完成后才能进入。

步骤：
1. 读取报告模板。
2. 根据已确认事实一次性生成最终 Markdown。
3. 通过 `scripts/build_output_path.py` 生成输出路径并创建月份目录。
4. 写入 `<output_root>/<YYYY-MM>/<YYYY-MM-DD>-<项目名>-<一句话总结>-项目资产解读.md`。
5. 在 `## 11｜真实运行与视觉验证` 中写入真实截图状态、运行方式、截图引用与校验结论。
6. 运行视觉证据 validator：

```bash
python scripts/validate_visual_evidence.py \
  "<visual-evidence.json>" \
  --screenshot-root "<screenshot_root>" \
  --expected-scale "<screenshot_scale>" \
  --report "<报告路径>"
```

7. 视觉 validator exit code 0 后，再运行最终报告 validator：

```bash
python scripts/validate_report.py \
  "<报告路径>" \
  --output-root "<output_root>" \
  --project-path "<当前项目绝对路径>" \
  --visual-evidence "<visual-evidence.json>"
```

8. 两个 validator 都为 exit code 0 才算完成。

一句话总结由 AI 在 TODO-01 阶段自动提炼，用于报告文件名和视觉资产目录名。

## 漂移阻断

视觉验证之外，任何阶段一旦开始进入以下方向，应立刻停止并回到当前 TODO：
- 修复项目
- 修改源码
- 升级依赖
- 修改依赖声明或 lockfile
- 大规模测试
- Git 清理
- 重构
- 全量源码摘要

视觉验证允许最小化启动、冻结依赖安装、浏览器打开与截图，但不得把资产解读任务变成开发调试任务。
