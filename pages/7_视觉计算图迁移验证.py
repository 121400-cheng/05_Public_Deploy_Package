"""Read-only display of verified real visual-graph evidence."""
from pathlib import Path
import sys
import json
import hashlib
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.ui import setup, footer

setup("视觉计算图迁移验证")
st.subheader("真实视觉网络迁移验证")
st.info("结果采用抽象计算代价进行调度验证，不代表特定 NPU/GPU 实测时间。")
st.caption("V3.0 · 已验证历史结果展示 · 本页不执行现场重新求解，不评价识别精度、FPS或能耗。")
data_root = Path(__file__).resolve().parents[1] / "data_public/vision/v30"
try:
    manifest = json.loads((data_root / "MANIFEST.json").read_text(encoding="utf-8"))
    content = (data_root / "demo.json").read_bytes()
    if hashlib.sha256(content).hexdigest().upper() != manifest["sha256"]:
        raise ValueError("Visual evidence integrity check failed")
    bundle = json.loads(content)
    if bundle["status"] != "TECHNICAL READY":
        raise ValueError("Visual evidence not validated")
except (OSError, ValueError, KeyError):
    st.error("视觉验证数据完整性检查未通过，请联系维护人员。")
    st.stop()

st.subheader("MobileNetV3-Small：轻量视觉网络")
mobile = bundle["mobile"]
cols = st.columns(3)
cols[0].metric("计算节点", mobile["compute_nodes"])
cols[1].metric("平均并行度", f'{mobile["P_avg"]:.1f}')
cols[2].metric("最大 ready", mobile["max_ready"])
st.write("任务级并行度有限：真实依赖图高度串行，增加计算核心不能直接获得任务级并行收益。")

st.subheader("GoogLeNet：多分支视觉网络")
network = bundle["googlenet"]
cols = st.columns(3)
cols[0].metric("计算节点", network["compute_nodes"])
cols[1].metric("平均并行度", f'{network["P_avg"]:.6f}')
cols[2].metric("最大 ready", network["max_ready"])
st.caption("采用 torchvision 公开结构，不加载预训练权重，使用推理模式，不训练。完整网络当前结果仍为单核；下面验证的是其中一个真实分支子图，不是完整模型多核加速。")

import networkx as nx
topology = network["topology"]
full_dag = nx.DiGraph()
full_dag.add_nodes_from(n["node_name"] for n in topology["nodes"])
full_dag.add_edges_from((e["source"], e["target"]) for e in topology["edges"])
levels = list(nx.topological_generations(full_dag))
layout = {name: (level, rank - (len(nodes)-1)/2) for level, nodes in enumerate(levels) for rank, name in enumerate(sorted(nodes))}
xx, yy = [], []
for a, b in full_dag.edges:
    xx.extend([layout[a][0], layout[b][0], None]); yy.extend([layout[a][1], layout[b][1], None])
overview = go.Figure(go.Scatter(x=xx, y=yy, mode="lines", line=dict(color="#b7c6d2", width=1), showlegend=False, hoverinfo="skip"))
overview.add_trace(go.Scatter(x=[layout[n["node_name"]][0] for n in topology["nodes"]],
    y=[layout[n["node_name"]][1] for n in topology["nodes"]], mode="markers", name="真实网络节点",
    marker=dict(size=5, color="#087f79"), text=[n["node_name"] for n in topology["nodes"]], hovertemplate="%{text}<extra></extra>"))
overview.update_layout(template="plotly_white", height=320, xaxis_title="真实依赖层级（非时间轴）", yaxis_title="分支布局", margin=dict(l=20,r=20,t=20,b=40))
st.plotly_chart(overview, width="stretch")
st.caption("完整网络真实分支拓扑概览。计算节点197，输入输出边界另列；未改变原依赖。")

st.subheader("真实 Inception 分支子图")
block = bundle["inception"]
metadata = block["metadata"]
profile = block["parallelism"]
st.write(f'Block：{metadata["block"]}；计算任务 {profile["compute_nodes"]} 个；4 个真实 branch；平均并行度 {profile["P_avg"]:.6f}；最大 ready {profile["max_ready"]}。')
st.caption(f'真实输入 shape：{metadata["input_shape"]}；输出 shape：{metadata["output_shape"]}。上游节点只提供边界输入，不重复执行其计算。')
positions = {metadata["upstream_input_node"]: (0, 1.5), metadata["join_node"]: (8, 1.5)}
colors = {}
palette = ["#163d60", "#087f79", "#ba7b28", "#755689"]
for row, (branch, names) in enumerate(metadata["branches"].items()):
    for index, name in enumerate(names):
        positions[name] = (1 + 6 * index / max(1, len(names) - 1), 3 - row)
        colors[name] = palette[row]
xs, ys = [], []
for edge in block["edges"]:
    a, b = positions[edge["source"]], positions[edge["target"]]
    xs.extend([a[0], b[0], None]); ys.extend([a[1], b[1], None])
fig = go.Figure(go.Scatter(x=xs, y=ys, mode="lines", line=dict(color="#b7c6d2", width=1.3),
                          hoverinfo="skip", showlegend=False))
for node in block["nodes"]:
    x, y = positions[node["node_name"]]
    fig.add_trace(go.Scatter(x=[x], y=[y], mode="markers", showlegend=False,
        marker=dict(size=11, color=colors.get(node["node_name"], "#384655")),
        text=[node["node_name"] + "<br>" + node["module_type"] + "<br>" + str(node["output_shape"])],
        hovertemplate="%{text}<extra></extra>"))
fig.update_layout(template="plotly_white", height=370, margin=dict(l=20,r=20,t=20,b=35),
                  xaxis=dict(title="真实分支结构布局（非时间轴）", showticklabels=False),
                  yaxis=dict(title="四个真实分支", tickvals=[3,2,1,0],
                             ticktext=["Branch 1","Branch 2","Branch 3","Branch 4"]))
st.plotly_chart(fig, width="stretch")
st.caption("连线全部来自完整网络的真实 FX 依赖；没有新增计算任务、删依赖或拆分卷积。")

defaults = [r for r in block["results"] if r["communication_factor"] == 1]
table = pd.DataFrame([{
    "配置核心数": r["num_cores"],
    "执行方式": "统一初始化（不执行搜索）" if r["num_cores"] == 1 else "确定性候选搜索",
    "初解 Makespan": r["baseline_makespan"],
    "结果 Makespan": r["optimized_makespan"],
    "活跃核心": r["active_cores"],
    "同配置初解降低率（%）": r["improvement"],
    "评价有效": r["valid"],
} for r in defaults])
st.dataframe(table, hide_index=True, width="stretch")
st.caption("默认 communication factor = 1.0；Makespan 单位为抽象 proxy cycles。降低率只比较同核心数、同通信场景下的初解与搜索结果。")
st.write("默认4核配置使用2个活跃核，20个计算任务分配为15/5/0/0，独立评价通过。")
st.warning("2 Core 最终结果144087优于当前4 Core结果154806。该实验说明多核收益取决于计算图并行性、任务粒度及跨核通信成本，并非核心数量越多越快。1 Core仅初始化，不能把本表解释为严格强扩展性能。")
with st.expander("通信代价敏感性（非实机参数）"):
    sensitivity = pd.DataFrame([{
        "通信系数": r["communication_factor"], "配置核心数": r["num_cores"],
        "活跃核心": r["active_cores"], "Makespan（抽象 cycles）": r["optimized_makespan"],
    } for r in block["results"]])
    st.dataframe(sensitivity, hide_index=True, width="stretch")
    st.caption("低通信场景可以出现多核，高通信场景会选择单核；不跨场景相减宣传性能提升。")
st.download_button("下载默认场景结果表", table.to_csv(index=False).encode("utf-8-sig"),
                   file_name="real_inception_default_results.csv", mime="text/csv")
st.subheader("工程结论")
st.write("计算图内在并行度和跨核通信代价共同决定多核调度收益；子图分区粒度同样影响分支并行的暴露。")
st.caption("已完成的是抽象资源模型下真实分支子图的调度验证；不代表真实芯片测试、工业设备接入或产线部署。")
footer()
