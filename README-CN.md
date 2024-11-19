# Luminarium

![GitHub Release](https://img.shields.io/github/release/AirTouch666/Luminarium)
![GitHub repo size](https://img.shields.io/github/repo-size/AirTouch666/Luminarium)
![Docker Build and Push dev](https://github.com/AirTouch666/Luminarium/actions/workflows/docker-build-push-dev.yml/badge.svg)

简体中文 | [English](./README.md)

## ⚡️关于

Luminarium 是一个简单的图床，使用 Python 开发，基于 Flask 框架。

## ✨功能

- 支持拖放上传和多文件选择
- 自动将上传的图片转换为 WebP 格式以节省空间
- 显示所有已上传图片的缩略图和链接
- 复制链接功能
- 支持自定义配置
- 多语言(beta)

## 💽安装
### 从 Docker 安装
#### 稳定版
   ```
   docker run -d -p {端口}:8080 airtouch/luminarium
   ```

#### 开发版
   ```
   docker run -d -p {端口}:8080 airtouch/luminarium-dev
   ```

### 从源码安装

1. 克隆仓库:
   ```
   git clone https://github.com/AirTouch666/Luminarium.git
   cd Luminarium
   ```

2. 安装依赖:
   ```
   pip install -r requirements.txt
   ```

3. 运行应用:
   ```
   python app.py
   ```

4. 在浏览器中打开 `http://{IP}:{PORT}`

## 🔧配置
应用程序使用 `config.json` 文件进行配置。首次运行时会自动创建此文件，包含以下默认设置：
```json
{
    "secret_key": "xxx",
    "port": 8080,//端口
    "background": "#f4f4f4",//背景
    "site_name": "Luminarium",//名称
    "site_icon": "",//图标
    "max_file_size": 10,//最大文件大小(MB)
    "allowed_extensions": ["png", "jpg", "jpeg", "gif", "webp"],//允许的文件类型
    "convert_to_webp": ["png", "jpg", "jpeg"],//自动转换为webp的文件类型
    "domain": ""//域名
}
```

您可以根据需要修改以下设置：
- `port`: 应用程序运行的端口号（默认为 8080）
- `background`: 应用程序的背景颜色或图片（默认为 #f4f4f4）
- `site_name`: 应用程序的名称（默认为 Luminarium）
- `site_icon`: 应用程序的图标（默认为空）
- `max_file_size`: 上传文件的最大大小（默认为 10MB）
- `allowed_extensions`: 允许上传的文件类型（默认为 ["png", "jpg", "jpeg", "gif", "webp"]）
- `convert_to_webp`: 自动转换为webp的文件类型（默认为 ["png", "jpg", "jpeg"]）
- `domain`: 域名（默认为空）

## ⌨️技术

- 后端: Python Flask
- 前端: HTML，CSS，JavaScript
- 图像处理: Pillow

## 🖥应用界面
![应用界面](./screenshots/1.png)
![应用界面](./screenshots/2.png)

## 🤝贡献

欢迎提交 Pull Requests 来改进这个项目。对于重大更改，请先开 issue 讨论您想要改变的内容。

## 📜许可证

本项目基于 MIT 许可证开源，详情见 [LICENSE](./LICENSE) 。