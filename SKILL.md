# Project Asset Insight Skill

## Purpose

对“当前项目”做长期知识资产解读，而不是运行审计。

第一目标始终是：

理解项目
→ 提炼核心能力
→ 发现值得借鉴的设计
→ 识别可直接复用 / 改造复用 / 思路复用的资产
→ 建立未来重新打开项目的触发场景与阅读路线
→ 输出 Obsidian 项目资产解读文档

## Not the goal

除非用户另行明确要求，否则不要主动：

- 安装依赖
- 启动项目
- 调试运行错误
- 修复 Bug
- 修改源码
- 重构项目
- 做 Git 审计
- 做测试覆盖分析
- 全量遍历并摘要所有文件

发现运行、构建、测试信息时，只能作为辅助事实，不得让报告围绕这些内容展开。

## Mandatory execution order

开始任务后，必须读取并遵守：

1. `references/workflow.md`
2. `references/analysis-rules.md`
3. `references/evidence-rules.md`
4. `references/metadata-rules.md`
5. `references/report-schema.md`

必须严格执行 TODO-00 → TODO-09。

TODO-01～TODO-08 完成前，不得生成最终 Markdown。

## Machine-level output config

机器级配置位置：

`%USERPROFILE%\\.project-asset-insight\\config.json`

若配置不存在，必须先执行 TODO-00：询问用户这台机器统一输出目录，并通过 `scripts/config_manager.py` 保存。

示例默认路径：`G:\YINCS 知识库\10 输入与素材\01 项目资产解读`

若配置存在且有效，直接读取 `output_root`，不得重复询问。

最终输出路径固定为：

`<output_root>\\<YYYY-MM>\\<YYYY-MM-DD>-<项目名称>-<一句话总结>-项目资产解读.md`

- YYYY-MM-DD 取当前实际日期
- 项目名称由当前项目实际识别
- 一句话总结由 AI 在 TODO-01 阶段自动提炼（限 30 字以内）
- 月份目录不存在时通过 `scripts/build_output_path.py --create-month-dir` 自动创建

## Completion gate

最终报告写入后，必须执行：

`python scripts/validate_report.py <报告路径> --output-root <output_root> --project-path <当前项目绝对路径>`

只有验证结果为 exit code 0 才算完成。

如果校验失败：修复报告后重新校验。
