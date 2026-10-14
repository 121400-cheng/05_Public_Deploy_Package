"""Public presentation chrome. Internal trace is available only in maintenance mode."""
from pathlib import Path
import os
import streamlit as st
from .data import display_instance

TITLE = "面向工业视觉检测场景的边缘 AI 多核推理调度与数据搬运优化系统"
SUBTITLE = "工业视觉边缘推理场景下的多核计算与存储访问优化原型"
PUBLIC_DISPLAY_MODE = os.environ.get("DEMO_PUBLIC_MODE", "1") != "0"
STYLE = (Path(__file__).resolve().parents[1] / "assets/style.css").read_text(encoding="utf-8")


def setup(page_title: str) -> None:
    st.set_page_config(page_title=f"{page_title}｜优化结果展示", layout="wide", initial_sidebar_state="expanded")
    st.markdown("<style>" + STYLE + "</style>", unsafe_allow_html=True)
    with st.sidebar:
        st.caption("计算与存储优化原型")
        st.markdown("**当前模式：已验证结果展示**")
        st.caption("当前页面展示已完成的算法验证结果，不执行现场重新求解。")
    st.markdown(f'<div class="demo-banner"><small>多核计算与存储访问优化</small><h2>{page_title}</h2><small>验证实例与方案回放</small></div>', unsafe_allow_html=True)


def source_note(scene: str, case_id: str) -> None:
    st.caption("数据来源：验证数据快照 ｜ " + display_instance(case_id))


def footer() -> None:
    st.divider()
    st.caption("Demo V3.0 ｜ 已验证结果展示与真实视觉分支验证")
