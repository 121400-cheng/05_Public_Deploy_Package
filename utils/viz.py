"""Charts show verified data and order slots, without deriving unverified timestamps."""
import networkx as nx
import plotly.graph_objects as go
from .data import display_instance

BLUE, TEAL, SLATE = "#1C4F80", "#0B8079", "#66788A"


def raw_graph(raw: dict, edge_limit: int = 48) -> go.Figure:
    edges = raw["edges"][:edge_limit]
    graph = nx.DiGraph((int(e["source"]), int(e["target"])) for e in edges)
    op_ids = {int(op["id"]) for op in raw["ops"]}
    pos = nx.spring_layout(graph, seed=0, iterations=80)
    ex, ey = [], []
    for u, v in graph.edges:
        ex += [pos[u][0], pos[v][0], None]
        ey += [pos[u][1], pos[v][1], None]
    fig = go.Figure(go.Scatter(x=ex, y=ey, mode="lines", line=dict(color="#B3C0CC", width=1), hoverinfo="skip", showlegend=False))
    for ids, label, color in (([n for n in graph if n in op_ids], "计算/搬运节点", BLUE), ([n for n in graph if n not in op_ids], "数据对象", TEAL)):
        fig.add_trace(go.Scatter(x=[pos[n][0] for n in ids], y=[pos[n][1] for n in ids], mode="markers+text", text=[str(n) for n in ids], textposition="top center", marker=dict(size=11, color=color), name=label, hovertemplate="节点编号 %{text}<extra>" + label + "</extra>"))
    fig.update_layout(title=f"输入依赖图节选（前 {len(edges)} 条依赖边）", plot_bgcolor="white", paper_bgcolor="white", height=430, margin=dict(l=20, r=20, t=55, b=20), xaxis=dict(visible=False), yaxis=dict(visible=False), legend=dict(orientation="h"))
    return fig


def core_order(plan: dict, title: str) -> go.Figure:
    fig = go.Figure()
    for core, schedule in enumerate(plan["core_schedules"]):
        if not schedule:
            continue
        xs = list(range(1, len(schedule) + 1))
        fig.add_trace(go.Scatter(x=xs, y=[core] * len(xs), mode="markers+text", text=[f"分组 {sg}" for sg in schedule], textposition="top center", marker=dict(size=22, color=TEAL if core % 2 else BLUE, symbol="square"), name=f"计算核心 {core}", hovertemplate="计算核心 " + str(core) + "<br>顺序位 %{x}<br>%{text}<extra></extra>"))
        if len(xs) > 1:
            fig.add_trace(go.Scatter(x=xs, y=[core] * len(xs), mode="lines", line=dict(color="#A9B7C5", width=1), hoverinfo="skip", showlegend=False))
    fig.update_layout(title=title + "：核心分配与执行顺序", xaxis_title="核内顺序位（非时间轴）", yaxis=dict(title="计算核心编号", tickmode="array", tickvals=[0, 1, 2, 3], autorange="reversed"), height=340, plot_bgcolor="white", paper_bgcolor="white", margin=dict(l=40, r=20, t=60, b=50), showlegend=False)
    return fig


def case_rates(df, title: str) -> go.Figure:
    values = df.sort_values("case_id")
    fig = go.Figure(go.Bar(x=values.case_id.map(display_instance), y=values.casewise_improvement_pct, marker_color=TEAL, name="逐实例降低率"))
    fig.add_hline(y=0, line_color=SLATE, line_dash="dash")
    fig.add_hline(y=float(values.casewise_improvement_pct.mean()), line_color="#BD5D22", annotation_text="平均逐实例降低率")
    fig.update_layout(title=title, xaxis=dict(title="验证实例（非时间序列）", tickmode="linear", dtick=10), yaxis_title="Makespan 降低率 (%)", plot_bgcolor="white", paper_bgcolor="white", height=430, showlegend=False)
    return fig
