from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
from utils.data import SCENES, case_table, display_instance, internal_trace, manifest, row
from utils.ui import setup, footer, PUBLIC_DISPLAY_MODE

setup("数据与复现说明")
meta = manifest()
cols = st.columns(4)
cols[0].metric("数据版本", meta["data_version"])
cols[1].metric("每模块验证实例", len(case_table("Q1")))
cols[2].metric("最近数据核验", meta["verified_on"])
cols[3].metric("结果状态", "已核验")
st.write("当前版本完成多核调度与数据搬运算法验证，并面向工业视觉边缘推理进行应用设计；真实视觉模型和边缘硬件接入属于后续验证内容。")
st.caption("核验日期是展示数据完整性与统计口径复核日期，不是实验运行日期。")

st.subheader("指标与统计口径")
st.table([
    {"指标": "Makespan（整体完成时间）", "含义": "计算图模型的整体执行周期", "单位": "cycles"},
    {"指标": "额外搬运量", "含义": "验证模型中的额外数据传输量", "单位": "bytes"},
    {"指标": "平均逐实例降低率", "含义": "各实例优化前后降低比例的算术平均", "单位": "%"},
])
st.subheader("验证实例追溯")
key = st.selectbox("技术模块", ["Q1", "Q2"], format_func=lambda item: SCENES[item]["name"])
df = case_table(key)
cid = st.selectbox("验证实例", df.case_id.tolist(), format_func=display_instance, index=df.case_id.tolist().index(SCENES[key]["case"]))
metric = row(key, cid)
st.table([
    {"项目": "实例", "内容": display_instance(cid)},
    {"项目": "数据来源", "内容": "验证数据快照"},
    {"项目": "优化前 / 优化后 Makespan", "内容": f"{int(metric.baseline_makespan_cycles):,} / {int(metric.optimized_makespan_cycles):,} cycles"},
])
with st.expander("内部数据追溯", expanded=False):
    if PUBLIC_DISPLAY_MODE:
        st.write("展示数据的源文件、源字段和完整校验记录保留于随包内部清单。公开模式只展示逻辑来源与验证实例编号。")
    else:
        st.json(internal_trace(key, cid))
st.subheader("完成度与复现范围")
st.table([
    {"功能": "调度与搬运模型", "状态": "已完成", "说明": "基准任务实例验证"},
    {"功能": "批量验证与可视化", "状态": "已完成", "说明": "每模块 100 个完整验证实例"},
    {"功能": "工业应用设计", "状态": "已完成映射", "说明": "执行层对象与目标应用对应"},
    {"功能": "真实模型与硬件接入", "状态": "待验证", "说明": "尚无端到端硬件实测"},
    {"功能": "生产线验证", "状态": "待验证", "说明": "尚无现场长期测试"},
])
st.write("本应用仅加载已完成的验证数据。独立部署包包含所有展示资源；现场求解和模型训练不在本界面中执行。")
st.caption("执行顺序图没有任务起止时间；数据指标也不用于换算真实 FPS、带宽或功耗。")
footer()
