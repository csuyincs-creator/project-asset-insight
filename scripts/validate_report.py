#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
from pathlib import Path

REQUIRED_META = [
    "编写来源", "编写主机", "文档初次编写时间", "文档版本号", "项目名称",
    "项目地址", "项目来源", "项目网址", "项目类型", "本地接触程度", "核心价值标签",
]

REQUIRED_SECTIONS = [
    "## 01｜30 秒看懂这个项目",
    "## 02｜它解决什么问题",
    "## 03｜核心能力",
    "## 04｜核心架构与实现思路",
    "## 05｜最值得借鉴的地方",
    "## 06｜可复用资产",
    "## 07｜可以进一步变成我的什么",
    "## 08｜什么时候值得重新打开它",
    "## 09｜15 分钟重新理解路线",
    "## 10｜哪些地方不用继续浪费时间",
    "## 11｜真实运行与视觉验证",
    "## 12｜最终资产结论",
]

PLACEHOLDERS = [
    "待填写", "TBD", "TODO", "xxx", "<项目名称>", "<实际值>", "<实际值或无法确认>",
]

BANNED_META_VALUES = {
    "自动识别", "自动生成", "GitHub / 官网 / 其他",
    "爬虫 / Agent / UI / 知识库 / Prompt / 自动化等",
    "仅收藏 / 已阅读 / 深入研究 / 已使用",
}

RUN_WORDS = ["安装", "构建", "报错", "修复", "启动失败", "依赖问题", "pytest", "npm run"]
ALLOWED_CAPTURE = {"CAPTURED", "NO_VISUAL_SURFACE", "CAPTURE_BLOCKED"}


def norm(p: str) -> str:
    return os.path.normcase(os.path.abspath(p))


def validate(report: Path, output_root: str | None, project_path: str | None, visual_evidence: Path):
    errors = []
    warnings = []

    if not report.exists() or not report.is_file():
        return [f"report not found: {report}"], warnings

    text = report.read_text(encoding="utf-8")
    if len(text.strip()) < 1000:
        errors.append("report is too short (<1000 characters)")

    for field in REQUIRED_META:
        m = re.search(rf"^\|\s*{re.escape(field)}\s*\|\s*(.*?)\s*\|\s*$", text, re.MULTILINE)
        if not m:
            errors.append(f"missing metadata field: {field}")
            continue
        value = m.group(1).strip()
        if not value:
            errors.append(f"empty metadata field: {field}")
        if value in BANNED_META_VALUES:
            errors.append(f"placeholder metadata value remains: {field}={value}")

    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"missing section: {section}")

    for ph in PLACEHOLDERS:
        if ph in text:
            errors.append(f"placeholder remains: {ph}")

    if project_path:
        if not os.path.exists(project_path):
            errors.append(f"project path does not exist: {project_path}")
        if project_path not in text:
            warnings.append("project path argument is not found literally in report text")

    if output_root:
        try:
            if os.path.isabs(output_root) and os.path.isabs(str(report)):
                if not norm(str(report)).startswith(norm(output_root)):
                    errors.append("report is outside output_root")
        except Exception:
            pass

    if not re.search(r"[A-Za-z0-9_.-]+[\\/][A-Za-z0-9_./\\-]+", text):
        errors.append("no evidence path detected in report")

    run_hits = sum(text.count(w) for w in RUN_WORDS)
    if run_hits >= 24:
        warnings.append("运行/故障相关词出现较多，请确认报告是否偏离项目资产解读目标")

    if not re.match(r"^\d{4}-\d{2}-\d{2}-.+?-项目资产解读\.md$", report.name):
        errors.append("filename must match: YYYY-MM-DD-<project>-<summary>-项目资产解读.md")
    if not re.fullmatch(r"\d{4}-\d{2}", report.parent.name):
        errors.append("parent directory must be YYYY-MM")

    if not visual_evidence.exists() or not visual_evidence.is_file():
        errors.append(f"visual evidence manifest not found: {visual_evidence}")
    else:
        try:
            manifest = json.loads(visual_evidence.read_text(encoding="utf-8"))
            status = manifest.get("capture_status")
            if status not in ALLOWED_CAPTURE:
                errors.append(f"invalid visual capture status: {status}")
            elif status not in text:
                errors.append(f"report does not state visual capture status: {status}")
        except Exception as exc:
            errors.append(f"invalid visual evidence manifest: {exc}")

    return errors, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("report")
    ap.add_argument("--output-root")
    ap.add_argument("--project-path")
    ap.add_argument("--visual-evidence", required=True)
    args = ap.parse_args()

    errors, warnings = validate(
        Path(args.report),
        args.output_root,
        args.project_path,
        Path(args.visual_evidence),
    )

    for w in warnings:
        print(f"WARNING: {w}")
    for e in errors:
        print(f"ERROR: {e}")

    if errors:
        sys.exit(1)
    print("OK: report validation passed")


if __name__ == "__main__":
    main()
