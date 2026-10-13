from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
import plotly.express as px
from utils.data import SCENES, case_table, public_table, summary
from utils.ui import setup, footer
from utils.viz import case_rates

setup("批量性能验证")
st.write("按两个技术模块分别汇总当前验证实例。改善率依据同实例、同配置、同评价口径下的优化前后数据计算。")
key = st.radio("技术模块", ["Q1", "Q2"], format_func=lambda item: SCENES[item]["name"], horizontal=True)
df, stat = case_table(key), summary(key)
cols = st.columns(4)
cols[0].metric("有效实例", stat["n"])
cols[1].metric("改善 / 持平 / 退化", f"{stat['improved']} / {stat['tied']} / {stat['regressed']}")
cols[2].metric("平均逐实例降低率", f"{stat['mean_pct']:.4f}%")
cols[3].metric("汇总指标降低率", f"{stat['pooled_pct']:.4f}%")
st.caption("平均逐实例率先分别求比例再平均；汇总率先求指标总量再求比例。两者权重不同。")
st.plotly_chart(case_rates(df, SCENES[key]["name"] + "｜逐实例改善率"), width="stretch")
table = public_table(key)
left, right = st.columns(2)
with left:
    ranked = table.nlargest(10, "Makespan 降低率（%）")
    fig = px.bar(ranked, x="实例", y="Makespan 降低率（%）", color_discrete_sequence=["#1C4F80"], title="改善率最高的 10 个实例")
    fig.update_layout(paper_bgcolor="white", plot_bgcolor="white")
    st.plotly_chart(fig, width="stretch")
with right:
    fig = px.histogram(table, x="Makespan 降低率（%）", nbins=20, color_discrete_sequence=["#0B8079"], title="实例改善率分布")
    fig.update_layout(yaxis_title="实例数", paper_bgcolor="white", plot_bgcolor="white")
    st.plotly_chart(fig, width="stretch")
st.subheader("逐实例结果")
st.dataframe(table, hide_index=True, width="stretch")
st.caption("单位：执行周期 cycles；数据搬运 bytes。两个模块分别评价，不直接比较不同模块的周期绝对值。")
footer()
