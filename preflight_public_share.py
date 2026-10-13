"""Check default public UI, portability and privacy; never starts a service."""
from __future__ import annotations
import argparse
import ast
from datetime import datetime, timezone, timedelta
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import sys
from types import SimpleNamespace
from unittest.mock import patch

FORBIDDEN = re.compile(r"(?i)\bQ[12]\b|问题[一二]|赛题|官方|Eval[12]|\bscene(?:\s+[AB])?\b")
WIN_PATH = re.compile(r"(?i)(?<![A-Za-z])[A-Z]:[\\/]")
USER_PATH = re.compile(r"(?i)C:[\\/]+Users[\\/]+[^\s\"']+")
EMAIL = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
CREDENTIAL = re.compile(r"(?i)\b(API_KEY|TOKEN|PASSWORD|SECRET)\b\s*[:=]\s*[\"']([^\"'\r\n]+)[\"']")
PRIVATE_IP = re.compile(r"\b(?:192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b")
SKIP = {".venv", "archive", "runtime_tmp", "__pycache__", ".pytest_cache", ".git", "data_snapshot", "logs"}


def active_files(root):
    for parent, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for name in names:
            path = Path(parent) / name
            if path.suffix in {".py", ".json", ".csv", ".toml", ".css", ".html", ".yaml", ".bat", ".ps1"} or name == "Dockerfile":
                if name not in {"preflight_public_share.py", "audit_public_text.py"}:
                    yield path


def privacy_scan(root):
    findings = []
    for path in active_files(root):
        for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
            for kind, regex in (("absolute path", WIN_PATH), ("user directory", USER_PATH), ("email", EMAIL), ("credential", CREDENTIAL), ("local IP", PRIVATE_IP)):
                if regex.search(line):
                    findings.append({"file": path.relative_to(root).as_posix(), "line": line_number, "kind": kind})
    return findings


def plot_text(spec):
    """Inspect displayed plot labels/tooltips, not Plotly's internal template keys."""
    text = []
    def walk(value, key=""):
        if key == "template":
            return
        if isinstance(value, dict):
            for k, v in value.items():
                walk(v, k)
        elif isinstance(value, list):
            for v in value:
                walk(v, key)
        elif isinstance(value, str) and key in {"text", "name", "hovertemplate", "hovertext", "ticktext", "label", "labels", "title"}:
            text.append(value)
    walk(json.loads(spec) if isinstance(spec, str) else spec)
    return text


def visible_text(app):
    pieces = []
    for kind in ("markdown", "caption", "title", "header", "subheader", "text", "code", "info", "warning", "success", "table", "dataframe", "metric", "json"):
        for element in app.get(kind):
            if kind == "metric":
                pieces.extend([str(element.label), str(element.value)])
            else:
                try:
                    pieces.append(str(element.value))
                except (AttributeError, KeyError, TypeError):
                    pieces.append(str(element.proto))
    for kind in ("selectbox", "radio"):
        for element in app.get(kind):
            pieces.append(str(element.label))
            pieces.extend(str(option) for option in element.options)
    for element in app.get("plotly_chart"):
        pieces.extend(plot_text(element.proto.spec))
    return "\n".join(pieces)


def ui_check(root, work_dir):
    os.environ["DEMO_PUBLIC_MODE"] = "1"
    sys.path.insert(0, str(root))
    temp = work_dir / "app_test"
    temp.mkdir(parents=True, exist_ok=True)
    with patch("tempfile.TemporaryDirectory", lambda *args, **kwargs: SimpleNamespace(name=str(temp))):
        from streamlit.testing.v1 import AppTest
    results = []
    for path in [root / "app.py", *sorted((root / "pages").glob("*.py"))]:
        app = AppTest.from_file(str(path), default_timeout=30).run()
        states = [("default", app)]
        texts = [visible_text(app)]
        if path.name.startswith(("2_", "3_", "6_")):
            app.selectbox[-1].select("case_001").run()
            states.append(("alternate instance", app))
            texts.append(visible_text(app))
        if path.name.startswith("4_"):
            app.radio[0].set_value("Q2").run()
            states.append(("alternate module", app))
            texts.append(visible_text(app))
        if path.name.startswith("6_"):
            app.selectbox[0].select("Q2").run()
            states.append(("alternate module", app))
            texts.append(visible_text(app))
        text = "\n".join(texts)
        hits = sorted({match.group(0) for match in FORBIDDEN.finditer(text)})
        results.append({
            "page": path.relative_to(root).as_posix(),
            "exceptions": sum(len(state.exception) for _, state in states),
            "forbidden_public_text": hits,
            "absolute_path_output": bool(WIN_PATH.search(text) or USER_PATH.search(text)),
            "internal_sha_output": bool(re.search(r"\b[0-9a-fA-F]{64}\b", text)),
            "local_ip_output": bool(PRIVATE_IP.search(text)),
        })
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--work-dir", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    report = args.report or root / "PUBLIC_SHARE_PREFLIGHT_REPORT.md"
    work = args.work_dir or root / "runtime_tmp/preflight_v17"
    requirement_rows = []
    for line in (root / "requirements.txt").read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.lstrip().startswith("#"):
            name, pinned = line.split("==")
            try:
                version = importlib.metadata.version(name)
            except importlib.metadata.PackageNotFoundError:
                version = "MISSING"
            requirement_rows.append((name, version, pinned, version == pinned))
    for path in active_files(root):
        if path.suffix == ".py":
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=path.name)
    privacy = privacy_scan(root)
    pages = ui_check(root, work)
    from utils import data, ui
    if data.DEMO.resolve() != root or not Path(ui.__file__).resolve().is_relative_to(root):
        raise RuntimeError("Wrong application root imported")
    meta = data.manifest()
    for key in data.SCENES:
        data.demo_case(key)
    stats = {key: data.summary(key) for key in data.SCENES}
    counts = {
        "Q1": sum("Q1" in hit.upper() for p in pages for hit in p["forbidden_public_text"]),
        "Q2": sum("Q2" in hit.upper() for p in pages for hit in p["forbidden_public_text"]),
        "source_terms": sum(("赛题" in hit or "官方" in hit or "问题" in hit) for p in pages for hit in p["forbidden_public_text"]),
        "Eval_Scene": sum(("eval" in hit.lower() or "scene" in hit.lower()) for p in pages for hit in p["forbidden_public_text"]),
    }
    passed = not privacy and all(ok for _, _, _, ok in requirement_rows) and all(p["exceptions"] == 0 and not p["forbidden_public_text"] and not p["absolute_path_output"] and not p["internal_sha_output"] and not p["local_ip_output"] for p in pages)
    payload = {"status": "PASS" if passed else "FAIL", "ui_visible_counts": counts, "requirements": requirement_rows, "pages": pages, "privacy_findings": privacy, "data_files": len(meta["files"]), "stats": stats}
    lines = ["# Demo V1.7 公开界面与独立运行检查", "", "结论：" + payload["status"], "", "模式：默认公开展示；检查首页、六页、其他实例及另一技术模块。内部变量、manifest 和本地审计名称允许保留，未当作页面文本。", "", "## 可见文字", "", " | 类别 | 命中 |", "|---|---:|"]
    lines += [f"| {key} | {count} |" for key, count in counts.items()]
    lines += ["", "## 页面与图表", "", "| 页面 | 异常数 | 内部名称命中 | 路径 / SHA / IP 输出 |", "|---|---:|---|---|"]
    lines += [f"| {p['page']} | {p['exceptions']} | {', '.join(p['forbidden_public_text']) or '0'} | {p['absolute_path_output']} / {p['internal_sha_output']} / {p['local_ip_output']} |" for p in pages]
    lines += ["", "## 依赖", "", "| 包 | 当前版本 | 固定版本 | 一致 |", "|---|---|---|---|"]
    lines += [f"| {name} | {current} | {pinned} | {ok} |" for name, current, pinned, ok in requirement_rows]
    lines += ["", f"数据清单：{len(meta['files'])} 份文件哈希通过；活动敏感扫描命中 {len(privacy)}。"]
    lines += [f"- FAIL：{f['file']}:{f['line']} ({f['kind']})" for f in privacy]
    lines += ["", "## 内部统计复核", ""]
    lines += [f"- {key}: {s['n']} / {s['improved']} / {s['tied']} / {s['regressed']}; mean={s['mean_pct']:.10f}%" for key, s in stats.items()]
    lines += ["", "旧归档、环境及日志不属于部署包或页面输入；人工核查资料公开许可仍由维护者完成。此检查不建立云服务，不保证托管平台可用率。"]
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    report.with_suffix(".json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PUBLIC_V17_PREFLIGHT={payload['status']} visible={counts} privacy={len(privacy)} pages={len(pages)}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
