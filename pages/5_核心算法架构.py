from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st
from utils.ui import setup, footer

setup("核心方法框架")
st.markdown("""<div class="notice" style="text-align:center;line-height:2.1">
输入任务实例<br>↓<br>任务及资源约束建模<br>↓<br>候选方案生成<br>↓<br>
方案评价与筛选<br>↓<br>
<b>计算侧：多核任务分配与执行顺序优化</b><br>＋<br>
<b>存储侧：数据驻留与搬运优化</b><br>↓<br>性能评价<br>↓<br>优化方案
</div>""", unsafe_allow_html=True)
left, right = st.columns(2)
with left:
    st.subheader("计算侧方法")
    st.write("关键路径感知初解、分组及分核邻域、可行性约束检查。候选经解析代理或排序模型筛选后，保留性能指标更优的方案。")
with right:
    st.subheader("存储侧方法")
    st.write("多起点初始化，结合跨分组通信、重复输入和存储压力评价候选；比较排序分支的候选方案并保留可行终案。")
st.subheader("搜索与候选筛选")
st.write("已有实现包括 Teacher 搜索、Student 排序与 Hybrid 路由。Top-K 只缩小需详细评价的候选集合；最终方案依据整体完成时间优先、额外搬运量次优的字典序判定。")
footer()
