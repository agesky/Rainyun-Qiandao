# 雨云自动签到（Web 面板版）

雨云每日自动签到工具，Docker 一键部署，配置统一走 Web 面板，支持多账户与自动续费。

## 功能特性

- ✅ 多账户管理（账号/密码/API Key/续费白名单）
- ✅ 定时签到（容器内 cron）
- ✅ 服务器到期检查与自动续费
- ✅ 多渠道通知（Web 高级设置）
- ✅ Docker 容器化部署

## 快速开始（Docker）

默认 `docker-compose.yml` 使用 GitHub Container Registry 预构建镜像，不需要在目标机器上本地构建。

```bash
# 1. 下载部署文件
curl -O https://raw.githubusercontent.com/Jielumoon/Rainyun-Qiandao/main/docker-compose.yml

# 2. 启动
docker compose up -d
```

打开浏览器访问：
```
http://localhost:8000
```

首次登录会初始化管理密码，后续使用该密码登录。

默认镜像：

```text
ghcr.io/jielumoon/rainyun-qiandao:latest
```

如需指定镜像版本，可在启动前设置：

```bash
RAINYUN_IMAGE=ghcr.io/jielumoon/rainyun-qiandao:<tag> docker compose up -d
```

## 开发构建

开发或本地改代码时使用 `docker-compose.dev.yml`，它会从当前源码构建镜像：

```bash
cp .env.example .env
docker compose -f docker-compose.dev.yml up -d --build
```

调试完停止：

```bash
docker compose -f docker-compose.dev.yml down
```

## 自动构建镜像

项目已配置 GitHub Actions：

- 推送到 `main`：构建并推送 `ghcr.io/jielumoon/rainyun-qiandao:latest`
- 推送 `v*` 标签：构建并推送对应版本标签
- Pull Request：只构建验证，不推送镜像
- 手动触发：支持在 GitHub Actions 页面运行 `Docker Image`
- 构建平台：`linux/amd64` 与 `linux/arm64`

首次使用 GHCR 时，请确认仓库的 `Settings -> Actions -> General -> Workflow permissions` 允许写入 packages；镜像可见性可在 GitHub Packages 页面调整。

## 版本发布

发布稳定版本时使用 Git tag，推荐格式为 `v主版本.次版本.修订号`，例如 `v3.1.0`：

```bash
git tag v3.1.0
git push origin v3.1.0
```

标签推送后，GitHub Actions 会自动构建并推送：

```text
ghcr.io/jielumoon/rainyun-qiandao:v3.1.0
```

用户可在 `.env` 中固定版本，避免 `latest` 自动跟随主分支：

```env
RAINYUN_IMAGE=ghcr.io/jielumoon/rainyun-qiandao:v3.1.0
```

## Web 面板说明

### 账户管理
- 添加账号、密码、API Key（用于服务器管理）
- 设置续费白名单（产品 ID 列表）
- 启用/禁用单个账户

### 系统设置
- 自动续费开关与阈值
- 定时表达式（cron），保存后自动写入 `/etc/cron.d/rainyun`

### 高级设置（建议）
- 通知渠道（`notify_channels` 数组，支持多通道）
- 跳过推送标题（换行分隔）
- 超时/重试/验证码/下载策略


## 环境变量（仅运行层）

> 业务配置已全部迁移至 Web 面板，env 只保留运行/部署参数。

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| WEB_ENABLED | true | Web 面板开关 |
| WEB_HOST | 0.0.0.0 | Web 绑定地址 |
| WEB_PORT | 8000 | Web 端口 |
| DATA_PATH | data/config.json | 数据文件路径 |
| CRON_MODE | true | 定时模式开关（默认开启） |
| CHROME_BIN | /usr/bin/chromium | Chromium 路径 |
| CHROMEDRIVER_PATH | /usr/bin/chromedriver | chromedriver 路径 |
| CHROME_LOW_MEMORY | false | 低内存模式 |

## 数据与备份

默认数据文件：`data/config.json`  
Cookies 存储：`data/cookies/`  
建议将 `./data` 挂载为 volume，避免容器重建丢失配置。

## 项目结构

```
rainyun/
├── web/              # FastAPI Web 面板与 API
│   ├── routes/       # 账户/服务器/系统设置/日志等接口
│   └── static/       # 前端页面（HTML/JS/CSS）
├── scheduler/        # 定时任务（cron 执行/多账户运行器）
├── browser/          # Selenium 浏览器（登录/签到/验证码）
├── notify/           # 多渠道通知（20+ 推送通道）
├── server/           # 服务器管理与自动续费
├── data/             # 数据模型与存储（Account/Settings）
└── api/              # 雨云 API 客户端封装
```

核心流程：
1. **定时任务**：cron 触发 → `scheduler/cron_runner.py` → 执行签到 + 续费 → 推送通知
2. **账号隔离**：每个账号独立 cookie 文件（`cookies_<id>.json`）
3. **通知渠道**：支持同时配置多个推送渠道（Server酱/TG/Bark等）

## 致谢

本项目基于以下仓库二次开发：

| 版本 | 作者 | 仓库 | 说明 |
|------|------|------|------|
| 原版 | SerendipityR | https://github.com/SerendipityR-2022/Rainyun-Qiandao | 初始 Python 版本 |
| 二改 | fatekey | https://github.com/fatekey/Rainyun-Qiandao | Docker 化改造 |
| 三改 | Jielumoon | 本仓库 | Web面板+多通知渠道+稳定性优化+自动续费 |

## 常见问题

### Nginx 反代到子路径（例如 `/rainyun/`）

如果你通过 `https://example.com/rainyun/` 访问，请确保做了两件事：

1. 访问入口必须带尾随斜杠（`/rainyun/`），建议把 `/rainyun` 301 到 `/rainyun/`。
2. 反代规则使用带尾随 `/` 的 `proxy_pass`，让 Nginx 去掉前缀后转发到容器的 `/`。

示例配置（按需补充 headers/超时等）：

```nginx
location = /rainyun {
    return 301 /rainyun/;
}

location = /favicon.ico {
    return 204;
}

location ^~ /rainyun/ {
    proxy_pass http://127.0.0.1:8000/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### 一键签到报 “Unable to obtain driver for chrome”
请确认容器内存在 chromedriver，并配置正确路径：
```
CHROME_BIN=/usr/bin/chromium
CHROMEDRIVER_PATH=/usr/bin/chromedriver
```

### cookies 在哪里
每个账号独立保存：`data/cookies/cookies_<account_id>.json`  
若账号未设置 ID，会用账号名/用户名哈希作为文件名。


### 修改 Web 设置后不生效
Web 设置会直接写入 `data/config.json`，无需重启容器。 
