# Streamlit Community Cloud 部署步骤

此文用于用户后续部署；本轮未创建仓库、上传数据或建立服务。

1. 将 `05_Public_Deploy_Package` **里面的文件**作为一个独立 Git 仓库根目录。确保根目录有 `app.py`、`requirements.txt`、`data_public/`、`utils/`、`pages/`、`assets/`、`.streamlit/`。不要上传原工程、虚拟环境、旧备份或运行日志。
2. 用户登录 Streamlit Community Cloud，并授权其访问准备好的仓库。
3. 点击 Create app，选择仓库、分支以及入口 `app.py`。
4. 在 Advanced settings 选择 **Python 3.11**，与当前经过验证的依赖环境保持一致。本应用不需要 Secrets；不要粘贴账号、token 或密码。
5. 点击 Deploy，查看依赖安装及服务日志。当前版本的五个直接依赖已固定；本轮没有在云端安装这些依赖，首次云端构建仍应核查日志。
6. 平台创建实际的 `streamlit.app` 地址后，依次检查首页、两个模块、批量页和数据页。不要把说明中的地址模板当作已经存在的 URL。
7. 用另一网络设备访问实际地址，并核对 100/88/12/2.7813% 和 100/97/3/9.4810% 等展示统计。确认后再分享。

云端托管不依赖原本地电脑保持开机；账号、平台运行策略和资源限制仍可能影响服务，不能承诺永久无间断访问。更新应用时只更新这个独立仓库；原工程不参与运行。

步骤依据：[Streamlit 官方部署文档](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)。
