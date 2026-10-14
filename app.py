"""Single Streamlit entry point for the self-contained public application."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st
from utils.data import summary
from utils.ui import TITLE, SUBTITLE, setup, footer


def home():
    setup("系统总览")
    st.title(TITLE)
    st.subheader(SUBTITLE)
    st.write("针对多核计算任务的执行调度与数据搬运问题进行建模和优化，通过批量基准实例验证效果，并面向工业视觉边缘推理进行应用设计。")
    for key in ("Q1", "Q2"):
        stat = summary(key)
        name = "多核任务调度优化" if key == "Q1" else "数据搬运与存储访问优化"
        st.subheader(name)
        cols = st.columns(4)
        cols[0].metric("有效实例", stat["n"])
        cols[1].metric("改善实例", stat["improved"])
        cols[2].metric("持平实例", stat["tied"])
        cols[3].metric("平均 Makespan 降低" if key == "Q1" else "平均指标降低", f"{stat['mean_pct']:.4f}%")
    st.caption("统计结果基于当前已验证批量实例。平均改善率采用逐实例降低率的算术平均。")
    st.write("多核任务调度与数据搬运优化可映射到边缘视觉推理计算图的执行层。技术定位和验证范围详见数据说明。")
    st.subheader("视觉网络计算图迁移证据")
    st.write("批量实例验证与真实视觉计算图迁移：MobileNetV3-Small 展示串行拓扑，GoogLeNet 的真实 Inception 分支子图通过多核分配验证。结果采用抽象代价，详见视觉计算图迁移验证。")
    footer()


navigation = st.navigation([
    st.Page(home, title="系统总览"),
    st.Page("pages/1_工业视觉检测场景.py", title="工业应用与技术定位"),
    st.Page("pages/2_多核推理调度优化.py", title="多核任务调度优化"),
    st.Page("pages/3_数据搬运优化.py", title="数据搬运与存储访问优化"),
    st.Page("pages/4_批量性能验证.py", title="批量性能验证"),
    st.Page("pages/5_核心算法架构.py", title="核心方法框架"),
    st.Page("pages/6_数据与复现说明.py", title="数据与复现说明"),
    st.Page("pages/7_视觉计算图迁移验证.py", title="视觉计算图迁移验证"),
])
navigation.run()
