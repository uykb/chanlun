# 缠论市场 WEB 分析工具 (数字货币版)

基于缠论的数字货币市场行情分析工具，主要针对币安 (Binance) 交易所。

## 功能特点

* **缠论图表展示**：自动计算并展示K线合并、分型、笔、线段、中枢、走势段等。
* **数字货币支持**：支持币安合约与现货市场。
* **行情监控**：实时监控背驰、买卖点，并可通过飞书或钉钉发送预警消息。
* **策略回测**：支持自定义缠论策略进行历史数据回测。
* **Docker部署**：简化安装过程，一键启动。

## 安装说明 (Docker)

项目仅支持 Docker 安装方式，以确保运行环境的一致性与稳定性。

### 1. 安装 Docker 与 Docker Compose

请确保您的系统中已安装 Docker 和 Docker Compose。

### 2. 克隆项目

```bash
git clone https://github.com/yijixiuxin/chanlun-pro.git
cd chanlun-pro
```

### 3. 配置环境变量

创建 `.env` 文件或直接在 `docker-compose.yml` 中修改配置。

主要配置项：
- `LOGIN_PWD`: WEB 登录密码 (留空则无需密码)
- `BINANCE_APIKEY`: 币安 API Key (用于实盘/资产查询)
- `BINANCE_SECRET`: 币安 API Secret
- `PROXY_HOST` & `PROXY_PORT`: 代理服务器配置 (如在国内环境访问币安需要配置)

### 4. 启动项目

```bash
docker-compose up -d
```

启动成功后，通过浏览器访问 `http://localhost:9900` 即可进入分析工具。

## 目录结构说明

- `data/`: 挂载到容器内的持久化数据目录，包含数据库、日志等。
- `src/chanlun/`: 核心缠论计算与逻辑代码。
- `web/`: WEB 界面相关代码。

## 注意事项

- 本项目目前主要针对 **数字货币 (CURRENCY)** 市场进行优化。
- 数据存储默认使用 SQLite，保存于 `data/` 目录下。
- 如需自定义策略，请参考 `src/chanlun/strategy/` 目录下的示例。


