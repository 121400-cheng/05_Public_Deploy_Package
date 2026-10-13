from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
from utils.data import SCENES, case_table, demo_case, display_instance, row
from utils.ui import setup, source_note, footer
from utils.viz import raw_graph, core_order

setup("多核任务调度优化")
st.caption("面向多核计算图执行的任务分配与执行顺序优化")
st.write("在任务依赖与资源约束下，确定计算任务分组、核心分配和核内顺序，降低 Makespan（整体完成时间）。")
df = case_table("Q1")
cid = st.selectbox("验证实例", df.case_id.tolist(), format_func=display_instance, index=df.case_id.tolist().index(SCENES["Q1"]["case"]))
r = row("Q1", cid)
base, opt = int(r.baseline_makespan_cycles), int(r.optimized_makespan_cycles)
cols = st.columns(4)
cols[0].metric("优化前 Makespan", f"{base:,} cycles")
cols[1].metric("优化后 Makespan", f"{opt:,} cycles")
cols[2].metric("绝对减少", f"{base-opt:,} cycles")
cols[3].metric("降低率", f"{r.casewise_improvement_pct:.4f}%")
st.caption("Makespan 为计算图模型的整体完成时间指标，按执行周期计量。")
st.write(f"额外搬运量：{int(r.baseline_added_ddr_bytes):,} → {int(r.optimized_added_ddr_bytes):,} bytes。")
if cid == SCENES["Q1"]["case"]:
    item = demo_case("Q1")
    raw = item["raw"]
    st.subheader("任务与数据依赖")
    st.write(f"计算/搬运节点 {len(raw['ops']):,} ｜ 数据对象 {len(raw['tensors']):,} ｜ 依赖边 {len(raw['edges']):,}")
    st.plotly_chart(raw_graph(raw), width="stretch")
    st.caption("依赖图仅展示输入的局部节选，未展示完整图。")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(core_order(item["baseline"], "优化前方案"), width="stretch")
    with right:
        st.plotly_chart(core_order(item["final"], "优化后方案"), width="stretch")
    st.caption("图示反映核心分配与顺序位；当前数据未提供可匹配的任务起止时间，不据此推算时间甘特图。")
else:
    st.info("该实例的验证指标完整；展示包未包含其输入和成对方案，当前只显示指标。")
source_note("Q1", cid)
footer()
