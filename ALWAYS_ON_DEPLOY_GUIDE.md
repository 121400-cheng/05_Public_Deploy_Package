# 独立云托管与长期访问

本机 localhost、同局域网地址和 Cloudflare 临时隧道均依赖运行 Demo 的本地电脑；关机后不能访问。应用要脱离本地电脑运行，须将独立包部署到云端。以下是已准备的部署路径，不表示已经建立服务，也不保证任何免费平台 100% 可用率。

## 方案 A：Streamlit Community Cloud

适合当前只读展示应用，部署入口为 `app.py`。用户将 `05_Public_Deploy_Package` 内容放入独立仓库，按 `DEPLOY_STREAMLIT_CLOUD.md` 选择仓库与 Python 3.11 后部署。平台提供应用地址并负责运行环境；无需维护服务器。本地关机不影响已经正常运行的云端实例，具体休眠、资源和服务策略仍取决于平台。

参考：[官方部署文档](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)。

## 方案 B：Render / Docker 服务器

独立包包含 `Dockerfile`、`.dockerignore` 和 `render.yaml`。Python 3.11 slim 镜像安装固定依赖，复制运行资源，以普通用户运行。启动监听 `0.0.0.0`，端口来自 `PORT`，未提供时才使用 8501。

Render 路径：用户先上传独立仓库，再从 Blueprint 读取 `render.yaml`，审核服务名称、区域、费用与套餐后手动创建。配置采用 Docker Web Service，健康检查为 `/_stcore/health`，没有账号或密钥。根据平台产生的真实 URL 检查页面；Render 的 PORT 无需在代码里写死。

通用 Docker 服务器可在该包根目录执行：

```text
docker build -t edge-scheduling-demo .
docker run --rm -e PORT=8501 -p 8501:8501 edge-scheduling-demo
```

若由平台指定其他 PORT，保持容器环境值与外部映射一致。长期 HTTPS、域名与可用性配置由托管服务或服务器维护者决定。本轮本机没有 Docker，镜像仅完成静态检查，构建/运行仍需在有 Docker 的环境验收。

参考：[Render Web Services 与端口规则](https://render.com/docs/web-services)、[Blueprint 配置](https://render.com/docs/blueprint-spec)、[Docker 服务](https://render.com/docs/docker)。

## 部署后验收

检查实际 URL、页面加载、两模块完整统计、图表、公开文字和来源显示。确认云端使用 `data_public`，不回读本地路径。公开内容没有访问认证时应只包含允许分享的展示材料；数据原始来源仍在内部 manifest 与技术文档保留。
