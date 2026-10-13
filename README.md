# 多核计算与存储访问优化展示应用

Demo V1.7。公开导航为：系统总览、工业应用与技术定位、多核任务调度优化、数据搬运与存储访问优化、批量性能验证、核心方法框架、数据与复现说明。

## 运行

在包含 `app.py` 的部署根目录，使用 Python 3.11 环境：

```text
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

展示数据、方案和 CSS 全部位于应用内的 `data_public`、`utils`、`assets`、`pages` 和 `.streamlit`。不需要原始工程、Solver、模型权重、数据库或 API 密钥。当前版本只展示已完成的算法验证结果，不执行现场求解。

`DEMO_PUBLIC_MODE` 默认 1。公开模式不显示内部编号/来源目录；如维护者在私有环境设置为 0，数据页的折叠追溯区可显示内部字段，仍不显示绝对本机路径。公开托管应保持默认值。

数据清单 `data_public/DATA_MANIFEST.json` 保存每个文件的来源、SHA256、用途与记录数。9 份展示数据逐字节复制自已核验副本，逐实例数值不因界面命名发生变化。核验日期指数据完整性与统计复核，不是新的实验运行时间。

## 内部技术来源说明

基准实例及验证结果来源于原“通用神经网络处理器下的多核调度问题”工程，内部 Q1/Q2、Eval1/Eval2 等标识仍保留于源字段、manifest 与原工程审计。普通 Web 页面采用技术模块名；这一改名不把仿真基准结果变成工业设备或生产线实测。正式申报的技术文档应准确披露原始来源。

原 Q2 报告文本与历史保护快照的差异仍保留在原工作包的版本说明中；本包使用已复算的结构化数据，不把文本差异解释为已修复。

## 云端运行

参见 `DEPLOY_STREAMLIT_CLOUD.md` 和 `ALWAYS_ON_DEPLOY_GUIDE.md`。Docker 启动兼容平台 `PORT` 环境变量，默认 8501。当前没有真实部署 URL，没有上传仓库或创建云服务。托管后无需本地电脑持续开机；平台可用率取决于服务与套餐。

## 检查

```text
python -m compileall .
python -m pytest tests -q
python preflight_public_share.py
```

pytest 是本地验证工具，不属于 Web 运行依赖。检查脚本默认在本地写检查报告；Web 页面不读这些报告。检查包括数据完整性、公开文字、页面加载与独立路径约束。
