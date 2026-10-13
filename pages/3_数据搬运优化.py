from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
from utils.data import SCENES, case_table, demo_case, display_instance, row
from utils.ui import setup, source_note, footer
from utils.viz import raw_graph, core_order

setup("数据搬运与存储访问优化")
st.caption("面向有限存储资源的数据驻留与搬运方案优化")
st.write("在存储约束和任务依赖下筛选方案。主要指标为 Makespan（整体完成时间），同时报告额外搬运字节。")
df = case_table("Q2")
cid = st.selectbox("验证实例", df.case_id.tolist(), format_func=display_instance, index=df.case_id.tolist().index(SCENES["Q2"]["case"]))
r = row("Q2", cid)
base, opt = int(r.baseline_makespan_cycles), int(r.optimized_makespan_cycles)
cols = st.columns(4)
cols[0].metric("优化前 Makespan", f"{base:,} cycles")
cols[1].metric("优化后 Makespan", f"{opt:,} cycles")
cols[2].metric("绝对减少", f"{base-opt:,} cycles")
cols[3].metric("降低率", f"{r.casewise_improvement_pct:.4f}%")
before, after = int(r.baseline_added_ddr_bytes), int(r.optimized_added_ddr_bytes)
cols = st.columns(3)
cols[0].metric("优化前额外搬运", f"{before:,} bytes")
cols[1].metric("优化后额外搬运", f"{after:,} bytes")
cols[2].metric("搬运量变化", f"{after-before:+,} bytes")
st.caption("额外搬运量为验证模型中的数据传输指标；不据此换算实机带宽、功耗或缓存命中率。")
if cid == SCENES["Q2"]["case"]:
    item = demo_case("Q2")
    raw = item["raw"]
    st.subheader("依赖与方案顺序")
    st.write(f"计算/搬运节点 {len(raw['ops']):,} ｜ 数据对象 {len(raw['tensors']):,} ｜ 依赖边 {len(raw['edges']):,}")
    st.plotly_chart(raw_graph(raw), width="stretch")
    st.caption("依赖图为输入的局部节选。")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(core_order(item["baseline"], "优化前方案"), width="stretch")
    with right:
        st.plotly_chart(core_order(item["final"], "优化后方案"), width="stretch")
    st.caption("显示核心分配与核内顺序；没有经验证的任务起止时间，因此不绘制时间甘特图。")
else:
    st.info("该实例的验证指标完整；展示包未包含其输入与成对方案，当前只显示指标。")
source_note("Q2", cid)
footer()
