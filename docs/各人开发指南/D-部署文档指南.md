# 陶柱宏 — 部署 + 文档 + 数据管道 + 集成测试

> 你的角色相当于半个组长。代码量最少，但掌控全局——Docker 环境、接口约定、文档统筹、质量保证。

## 你需要做的事

| 序号 | 任务 | 产出 |
|------|------|------|
| 1 | Docker Compose 一键部署 | `deploy/docker-compose.yml` + 4个 Dockerfile |
| 2 | Nginx 反向代理 | `deploy/nginx.conf` |
| 3 | 数据采集管道 | `data-pipeline/` 定时抓天气和价格 |
| 4 | **文档主笔** | 四份文档（需求规格、系统设计、接口、测试报告） |
| 5 | 集成测试 | `tests/` E2E 测试 |
| 6 | GitHub 仓库管理 | Issue、分支保护、PR Review |

## 开发顺序

1. **第1天**：读完全部文档，确认 Docker 能用 → 写 docker-compose.yml 骨架
2. **第2-3天**：写 Dockerfile（前端/后端/AI/MySQL 各一个）
3. **第4-5天**：数据采集管道（Python 脚本 + 定时任务）
4. **同时进行**：边等其他人代码，边写四份文档的初稿
5. **后期**：等 B、C、A 的代码能跑 → 集成测试 → 完善文档 → 准备答辩

---

## 一、Docker Compose 配置

### 1.1 项目结构

```
deploy/
├── docker-compose.yml
├── nginx.conf
├── frontend.Dockerfile
├── backend.Dockerfile
├── ai-service.Dockerfile
└── .env                  # 数据库密码等敏感信息
```

### 1.2 前端 Dockerfile (`deploy/frontend.Dockerfile`)

```dockerfile
# 构建阶段
FROM node:18-alpine AS builder
WORKDIR /app
COPY ../frontend/package*.json ./
RUN npm install
COPY ../frontend/ .
RUN npm run build

# 运行阶段
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 1.3 后端 Dockerfile (`deploy/backend.Dockerfile`)

```dockerfile
FROM openjdk:17-slim
WORKDIR /app
COPY ../backend/target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

### 1.4 AI 服务 Dockerfile (`deploy/ai-service.Dockerfile`)

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY ../ai-service/requirements.txt .
RUN pip install -r requirements.txt
COPY ../ai-service/ .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 1.5 docker-compose.yml

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: agriculture-mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: agriculture
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ../docs/schema.sql:/docker-entrypoint-initdb.d/schema.sql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: agriculture-redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      retries: 5

  minio:
    image: minio/minio:latest
    container_name: agriculture-minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

  ai-service:
    build:
      context: ..
      dockerfile: deploy/ai-service.Dockerfile
    container_name: agriculture-ai
    ports:
      - "8000:8000"
    depends_on:
      mysql:
        condition: service_healthy

  backend:
    build:
      context: ..
      dockerfile: deploy/backend.Dockerfile
    container_name: agriculture-backend
    ports:
      - "8080:8080"
    environment:
      SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/agriculture?useUnicode=true&characterEncoding=utf-8&serverTimezone=Asia/Shanghai
      SPRING_DATASOURCE_USERNAME: root
      SPRING_DATASOURCE_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      AI_SERVICE_URL: http://ai-service:8000
      MINIO_ENDPOINT: http://minio:9000
    depends_on:
      mysql:
        condition: service_healthy
      ai-service:
        condition: service_started

  frontend:
    build:
      context: ..
      dockerfile: deploy/frontend.Dockerfile
    container_name: agriculture-frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  mysql_data:
  minio_data:
```

### 1.6 Nginx 配置 (`deploy/nginx.conf`)

```nginx
server {
    listen 80;
    server_name localhost;

    # 前端静态文件
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 代理到后端
    location /api/ {
        proxy_pass http://backend:8080/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 1.7 .env 文件

```env
MYSQL_ROOT_PASSWORD=agriculture2026
MINIO_USER=admin
MINIO_PASSWORD=admin123456
```

### 启动命令

```bash
cd deploy
docker compose up -d           # 启动所有服务
docker compose ps               # 查看运行状态
docker compose logs -f backend  # 查看后端日志
docker compose down             # 停止并删除
```

---

## 二、数据采集管道

```
data-pipeline/
├── weather_collector.py   # 天气数据采集
├── price_collector.py     # 市场价格采集
├── scheduler.py           # 定时任务调度
└── requirements.txt
```

### 2.1 天气采集 (`data-pipeline/weather_collector.py`)

```python
"""
模拟天气采集。实际可对接中国天气网API或公开气象数据。
"""
import httpx
import random
from datetime import datetime, timedelta

# 昆明呈贡的近7天模拟天气
def collect_weather(location: str = "昆明呈贡"):
    """采集天气数据"""
    records = []
    for i in range(7):
        date = (datetime.now() - timedelta(days=6-i)).strftime("%Y-%m-%d")
        records.append({
            "location": location,
            "record_date": date,
            "temperature": round(random.uniform(18, 28), 1),
            "humidity": round(random.uniform(50, 90), 1),
            "rainfall": round(random.uniform(0, 25), 1),
            "wind_speed": round(random.uniform(0.5, 5.0), 1),
            "weather_desc": random.choice(["晴", "多云", "阴", "小雨", "阵雨"]),
            "data_source": "模拟数据"
        })
    return records

# 实际使用时可替换为：
# async def collect_weather_real():
#     url = "https://devapi.qweather.com/v7/weather/7d"
#     ...
```

### 2.2 价格采集 (`data-pipeline/price_collector.py`)

```python
"""市场价格采集。实际可从农业农村部网站或公开行情API抓取。"""
import random
from datetime import datetime, timedelta

def collect_prices(crop_type: str = "番茄"):
    """采集市场价格"""
    records = []
    for i in range(30):
        date = (datetime.now() - timedelta(days=29-i)).strftime("%Y-%m-%d")
        base_price = 3.5 if crop_type == "番茄" else 4.0
        records.append({
            "crop_type": crop_type,
            "price": round(base_price + random.uniform(-1.0, 1.5), 1),
            "unit": "元/公斤",
            "market": "呈贡龙城农贸市场",
            "record_date": date,
            "data_source": "模拟数据"
        })
    return records
```

### 2.3 定时调度 (`data-pipeline/scheduler.py`)

```python
"""使用 schedule 库实现定时采集"""
import schedule
import time
import httpx

API_BASE = "http://localhost:8080/api"

def sync_weather():
    """每天6点同步天气"""
    from weather_collector import collect_weather
    records = collect_weather()
    # POST到后端接口
    response = httpx.post(f"{API_BASE}/weather/batch", json=records)
    print(f"天气同步完成: {len(records)}条")

def sync_prices():
    """每天早上8点同步价格"""
    from price_collector import collect_prices
    for crop in ["番茄", "辣椒", "花卉"]:
        records = collect_prices(crop)
        response = httpx.post(f"{API_BASE}/market-prices/batch", json=records)
        print(f"{crop}价格同步完成: {len(records)}条")

# 定时任务
schedule.every().day.at("06:00").do(sync_weather)
schedule.every().day.at("08:00").do(sync_prices)

if __name__ == "__main__":
    print("数据采集管道启动...")
    # 首次立即执行
    sync_weather()
    sync_prices()
    # 进入循环
    while True:
        schedule.run_pending()
        time.sleep(60)
```

---

## 三、四份文档撰写要点

### 文档1：需求规格说明书
**你在其中的角色**：主笔。A/B/C 提供各自模块的功能描述。

**大纲**：
1. 项目背景（云南特色农业 + AI 诊断需求）
2. 用户角色与故事（农户/农技人员/合作社管理/管理员，各2-3条）
3. 用例图（用 PlantUML 或 Draw.io 画）
4. 功能需求（按模块列：地块管理、图像识别、RAG诊断、农事任务、数据看板）
5. 非功能需求（响应时间<3s、图片<10MB、准确率>80%）

### 文档2：系统设计说明书
**大纲**：
1. 系统架构图（前端 → Nginx → 后端 → AI服务 → 数据库）
2. ER 图（用数据库设计里的表，Draw.io 画）
3. 时序图（核心流程：用户上传图片 → 后端转发AI → AI返回结果 → 前端展示）
4. 部署图（Docker Compose 各容器的关系）
5. 技术选型说明（为什么选这个技术栈）

### 文档3：前后端接口文档
**直接用 `docs/API接口文档.md`**，不用重写。你负责确保 B 和 A 的实现与文档一致。

### 文档4：测试报告
**大纲**：
1. 前端测试（A 提供：Vitest 单元测试结果截图）
2. 后端测试（B 提供：JUnit 测试结果截图）
3. 接口测试（你负责：用 Postman/Apifox 测试所有接口，导出报告）
4. AI 效果测试（C 提供：准备20张测试图片，统计识别准确率、拒识率）
5. 性能测试（可选：JMeter 压测登录接口）

---

## 四、集成测试

### 端到端测试流程

```
1. 用管理员账号登录
2. 创建农场 "测试农场"
3. 在农场下创建地块 "测试地块1号"
4. 在地块上登记作物 "番茄-粉果1号"
5. 上传一张病害图片
6. 等待诊断结果返回（确认状态从 processing → completed）
7. 查看诊断结果（识别结果 + 防治建议 + Agent研判）
8. 确认自动生成了农事任务
9. 用农技人员账号登录，审核诊断结果
10. 查看数据看板页面
```

你用 Postman/Apifox 把这10步跑通，截图放进测试报告。

---

## 五、GitHub 仓库管理

1. **创建仓库**：在 GitHub 创建 `agriculture-diagnosis`，邀请另外三人
2. **分支保护**：Settings → Branches → 保护 main 分支（需要 PR 才能合并）
3. **初始化仓库**：
```bash
git init
git add .
git commit -m "init: 项目初始化 + 团队指导文档"
git branch -M main
git remote add origin https://github.com/你们组/agriculture-diagnosis.git
git push -u origin main
```
4. **创建 Issue**：把10个开发阶段做成 Issue，分配给对应的人
5. **PR Review**：每个人合并前你先看一眼，确保不冲突

---

## 关键时刻

- **第1天**：确认 Docker 能用（如果不能用 → 先不管 Docker，大家本地开发，最后统一部署）
- **每周检查**：每个人进度如何，接口有没有改
- **提交前2天**：docker compose up 一把梭，确认全部服务能启动
