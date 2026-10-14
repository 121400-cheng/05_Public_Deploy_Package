"""Read-only public data access; historical identifiers stay inside this module."""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
import re

import pandas as pd

DEMO = Path(__file__).resolve().parents[1]
PUBLIC_DATA = DEMO / "data_public"
SCENES = {
    "Q1": {
        "name": "多核任务调度优化", "case": "case_017",
        "csv": PUBLIC_DATA / "metrics/scheduling_results.csv",
        "raw": PUBLIC_DATA / "scheduling/instance_017/input.json",
        "baseline_plan": PUBLIC_DATA / "scheduling/instance_017/baseline.json",
        "final_plan": PUBLIC_DATA / "scheduling/instance_017/optimized.json",
        "initial_field": "initial_makespan", "final_field": "final_makespan",
    },
    "Q2": {
        "name": "数据搬运与存储访问优化", "case": "case_057",
        "csv": PUBLIC_DATA / "metrics/movement_results.csv",
        "raw": PUBLIC_DATA / "movement/instance_057/input.json",
        "baseline_plan": PUBLIC_DATA / "movement/instance_057/baseline.json",
        "final_plan": PUBLIC_DATA / "movement/instance_057/optimized.json",
        "initial_field": "initial_T", "final_field": "Portfolio_Final_T",
    },
}


def display_instance(case_id: str) -> str:
    match = re.fullmatch(r"case_(\d{3})", case_id)
    if not match:
        raise ValueError("实例编号格式无效")
    return "实例 " + match.group(1)


@lru_cache(maxsize=1)
def manifest() -> dict:
    value = json.loads((PUBLIC_DATA / "DATA_MANIFEST.json").read_text(encoding="utf-8"))
    files = value["files"]
    if len(files) != 10 or len({entry["public_file"] for entry in files}) != 10:
        raise ValueError("验证数据清单异常")
    for entry in files:
        path = (PUBLIC_DATA / entry["public_file"]).resolve()
        if not path.is_relative_to(PUBLIC_DATA.resolve()):
            raise ValueError("验证数据路径异常")
        if hashlib.sha256(path.read_bytes()).hexdigest().upper() != entry["sha256"]:
            raise ValueError("验证数据完整性检查未通过")
    return value


@lru_cache(maxsize=2)
def case_table(scene: str) -> pd.DataFrame:
    manifest()
    df = pd.read_csv(SCENES[scene]["csv"], encoding="utf-8")
    expected = {f"case_{i:03d}" for i in range(1, 101)}
    if len(df) != 100 or set(df["case_id"]) != expected or df["case_id"].duplicated().any():
        raise ValueError("验证实例覆盖或唯一性异常")
    for col in ("baseline_makespan_cycles", "optimized_makespan_cycles", "baseline_added_ddr_bytes", "optimized_added_ddr_bytes"):
        if df[col].isna().any():
            raise ValueError("验证指标有缺失")
    if (df["baseline_makespan_cycles"] <= 0).any() or (df["optimized_makespan_cycles"] <= 0).any():
        raise ValueError("整体完成时间指标必须为正")
    rate = 100 * (df["baseline_makespan_cycles"] - df["optimized_makespan_cycles"]) / df["baseline_makespan_cycles"]
    if ((rate - df["casewise_improvement_pct"]).abs() > 1e-8).any():
        raise ValueError("实例改善率与基础指标不一致")
    return df.sort_values("case_id").reset_index(drop=True)


def summary(scene: str) -> dict:
    df = case_table(scene)
    base, opt = df["baseline_makespan_cycles"], df["optimized_makespan_cycles"]
    return {
        "n": len(df), "improved": int((opt < base).sum()),
        "tied": int((opt == base).sum()), "regressed": int((opt > base).sum()),
        "mean_pct": float(df["casewise_improvement_pct"].mean()),
        "pooled_pct": float(100 * (base.sum() - opt.sum()) / base.sum()),
    }


def row(scene: str, case_id: str) -> pd.Series:
    values = case_table(scene).loc[lambda d: d.case_id == case_id]
    if len(values) != 1:
        raise ValueError("验证实例不存在")
    return values.iloc[0]


@lru_cache(maxsize=16)
def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def demo_case(scene: str) -> dict:
    cfg = SCENES[scene]
    metrics = row(scene, cfg["case"])
    raw = read_json(cfg["raw"])
    original = read_json(cfg["baseline_plan"])
    before = original["initial_plan"] if scene == "Q1" else original
    after = read_json(cfg["final_plan"])
    if scene == "Q1":
        if int(original["initial_makespan"]) != int(metrics.baseline_makespan_cycles) or int(original["initial_added_ddr"]) != int(metrics.baseline_added_ddr_bytes):
            raise ValueError("初始方案与验证指标不一致")
    else:
        initial = read_json(PUBLIC_DATA / "movement/instance_057/baseline_result.json")
        official = initial["official_result"]
        if initial["label"] != "W3" or int(official["makespan"]) != int(metrics.baseline_makespan_cycles) or int(official["added_copy_bytes"]) != int(metrics.baseline_added_ddr_bytes):
            raise ValueError("初始方案与验证指标不一致")
    for plan in (before, after):
        if set(plan) != {"node_to_subgraph", "core_schedules"} or len(plan["core_schedules"]) != 4:
            raise ValueError("展示方案结构异常")
    return {"id": cfg["case"], "row": metrics, "raw": raw, "baseline": before, "final": after, "cfg": cfg}


def public_table(scene: str) -> pd.DataFrame:
    df = case_table(scene)
    return pd.DataFrame({
        "实例": df.case_id.map(display_instance),
        "优化前 Makespan（cycles）": df.baseline_makespan_cycles,
        "优化后 Makespan（cycles）": df.optimized_makespan_cycles,
        "Makespan 降低率（%）": df.casewise_improvement_pct,
        "优化前额外搬运（bytes）": df.baseline_added_ddr_bytes,
        "优化后额外搬运（bytes）": df.optimized_added_ddr_bytes,
    })


def internal_trace(scene: str, case_id: str) -> dict:
    metrics = row(scene, case_id)
    return {
        "module": scene, "case_id": case_id, "source": str(metrics.source_path),
        "baseline_field": str(metrics.initial_field),
        "optimized_field": str(metrics.final_field),
    }
