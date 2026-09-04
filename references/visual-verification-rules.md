# 强制视觉验证规则

## 目标

视觉验证用于回答一个源码阅读无法替代的问题：这个项目真实运行后到底长什么样、核心界面是否真的存在、页面是否正常渲染。

视觉验证属于项目资产解读证据链的一部分，不等同于功能测试或开发调试。

## 核心原则

1. 只要项目存在任何可视界面，就必须截图。
2. 截图能力与视觉理解能力解耦。
3. Agent 没有看图能力，不得成为跳过截图的理由。
4. 只有项目本身不存在可视界面，或经过规定的运行与回退尝试后仍客观无法渲染，才允许没有截图。
5. 视觉验证不得修改目标项目源码，不得为了“让它跑起来”而开发或修复项目。

## 机器级截图配置

首次使用或旧配置缺字段时，必须询问用户：

- `screenshot_root`：截图资产根目录，必须是绝对路径。
- `screenshot_scale`：截图缩放倍率，允许 `0.5`～`4.0`。常见选择为 `1 / 1.5 / 2 / 3`，但不得替用户静默选择默认值。

用户可以明确选择让 `screenshot_root` 与 `output_root` 相同，也可以指定独立目录。

配置保存在：

`%USERPROFILE%\.project-asset-insight\config.json`

## 截图资产目录

固定为：

`<screenshot_root>/<YYYY-MM>/<YYYY-MM-DD>-<项目名称>-<一句话总结>-项目资产解读.assets/`

目录至少包含：

- `visual-evidence.json`
- 存在可视界面且截图成功时，至少一张截图，例如 `01-overview.png`

推荐命名：

- `01-overview.png`：项目主界面 / 核心视觉入口
- `02-core-feature.png`：核心功能界面
- `03-secondary-feature.png`：第二重要界面
- `04-settings.png`：设置或配置界面

不要为了数量硬凑截图。单页项目 1 张即可；多核心页面一般 2～4 张。

## TODO-09A｜视觉界面探测

必须检查项目是否存在可视界面。不能只看 README。

优先检查：

- `index.html`
- `src/App.*`
- `app/`
- `pages/`
- `public/`
- `static/`
- `templates/`
- `examples/`
- `demo/`
- Storybook / docs demo
- Electron / Tauri / Flutter / Qt
- Gradio / Streamlit
- Canvas / SVG / WebGL / Three.js
- 项目文档中明确提供的官方 Demo

允许的最终判断：

- `CAPTURED`
- `NO_VISUAL_SURFACE`
- `CAPTURE_BLOCKED`

禁止使用模糊状态，例如“暂未截图”“不方便截图”“环境可能不支持”。

## TODO-09B｜运行与截图

只要确认存在可视界面，就必须尝试打开。

推荐顺序：

1. 当前环境已经运行的页面或现成预览。
2. 项目官方声明的启动命令。
3. 静态 HTML 直接打开。
4. 项目自带 demo / examples / Storybook / preview。
5. Agent 自带浏览器或截图工具。
6. 项目已经存在的 Playwright / Puppeteer 能力。
7. Skill 自带 `scripts/capture_visual.py`，调用本机 Chrome / Chromium / Edge headless 截图。
8. 官方 hosted demo，仅作为本地版本无法运行后的补充证据，并必须标记为外部 Demo。

### 允许的最小化运行行为

为了视觉验证，允许：

- 启动项目已有 dev / preview / demo 命令
- 打开静态 HTML
- 使用项目已经存在的依赖环境
- 安装项目 manifest / lockfile 已明确声明的依赖，但优先使用冻结安装
- 创建临时 venv 或临时运行目录
- 使用浏览器 headless 模式

冻结安装示例：

- `npm ci`
- `pnpm install --frozen-lockfile`
- `yarn install --immutable`

### 仍然禁止

- 修改目标项目源码
- 修改 `package.json` / `pyproject.toml` 等依赖声明
- 修改 lockfile
- 升级依赖以解决兼容性问题
- 修 Bug
- 重构
- 运行具有破坏性的数据库迁移
- 调用真实支付、发信、删除、发布等生产副作用
- 为了截图而伪造不存在的 UI

原则：可以“为了看它长什么样而运行”，不能“为了让它跑起来而开发它”。

## TODO-09C｜机器级校验

截图生成后至少检查：

- 截图文件真实存在
- 文件大小合理
- PNG 尺寸合理
- `screenshot_scale` 与机器配置一致
- Markdown 最终引用截图文件
- `visual-evidence.json` 存在

若 Agent / 浏览器工具支持，还应记录：

- 页面 URL
- viewport
- `document.readyState`
- Console Error
- Page Error
- Failed Request
- HTTP 4xx / 5xx
- 水平溢出
- 页面主体是否为空

## TODO-09D｜视觉语义复核

若 Agent 具备视觉理解能力，必须重新查看已经生成的截图，并检查：

- 页面是否正常渲染
- 是否为空白页
- 是否出现异常黑块
- 是否有明显遮挡或元素重叠
- 是否存在文字截断
- 是否存在明显越界 / viewport 溢出
- 核心 UI 是否与源码分析一致
- 最值得记住的视觉特征是什么

若 Agent 不具备视觉理解能力：

- 截图仍然必须生成
- 机器级校验仍然必须执行
- `review_status` 写为 `VISION_UNAVAILABLE`
- 不得假装已经看过图片

## 视觉证据等级

- `L0`：没有截图，仅适用于 `NO_VISUAL_SURFACE` 或经证明的 `CAPTURE_BLOCKED`
- `L1`：截图文件成功生成并通过文件级校验
- `L2`：L1 + 浏览器 / DOM / Console / Network 等运行时自动校验
- `L3`：L2 或 L1 + Agent 对截图完成视觉语义复核

`CAPTURED` 至少必须达到 `L1`。

## visual-evidence.json

截图成功示例：

```json
{
  "schema_version": "1.0",
  "capture_status": "CAPTURED",
  "review_status": "VISION_REVIEWED",
  "verification_level": "L3",
  "asset_dir": "G:/.../project.assets",
  "source_url": "http://127.0.0.1:5173",
  "viewport": {"width": 1440, "height": 900},
  "screenshot_scale": 2.0,
  "screenshots": [
    {"path": "01-overview.png", "purpose": "overview"}
  ],
  "runtime_checks": {
    "console_errors": 0,
    "page_errors": 0,
    "failed_requests": 0,
    "horizontal_overflow": false
  }
}
```

没有可视界面示例：

```json
{
  "schema_version": "1.0",
  "capture_status": "NO_VISUAL_SURFACE",
  "review_status": "VISION_UNAVAILABLE",
  "verification_level": "L0",
  "reason": "该项目是纯 CLI / library，没有 Web、GUI、demo 或其他可视入口。",
  "checked_entries": ["README.md", "pyproject.toml", "src/"],
  "evidence": ["README 明确说明仅提供命令行能力", "项目目录未发现 UI 入口"]
}
```

截图客观阻塞示例：

```json
{
  "schema_version": "1.0",
  "capture_status": "CAPTURE_BLOCKED",
  "review_status": "VISION_UNAVAILABLE",
  "verification_level": "L0",
  "reason": "存在 Web UI，但当前环境在规定回退路径后仍无法渲染。",
  "capture_attempts": [
    {"method": "official-start-command", "success": false}
  ],
  "fallbacks_checked": ["static-html", "demo", "local-browser", "official-demo"],
  "errors": ["实际错误信息"]
}
```

## CAPTURE_BLOCKED 的硬条件

以下理由单独出现时，不足以判定 `CAPTURE_BLOCKED`：

- 没安装依赖
- README 没写启动方式
- 第一次启动失败
- 端口冲突
- Agent 没有内置浏览器
- Agent 不能看图
- 截图工具不方便

必须留下真实尝试记录和回退检查记录。

## Completion Gate

TODO-10 完成前必须执行：

```bash
python scripts/validate_visual_evidence.py \
  "<visual-evidence.json>" \
  --screenshot-root "<screenshot_root>" \
  --report "<报告路径>"
```

只有 exit code `0` 才能继续最终报告验收。
