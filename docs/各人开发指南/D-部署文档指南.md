# 陶柱宏 — 部署 + 文档 + 数据管道 + 集成测试

> ⚠️ **李珈逾的 AI 服务已全部完成并测试通过。你部署时 AI 服务容器需要安装 PyTorch/Transformers 依赖，镜像会比较大（~2GB）。**

## 你需要做的事

| 序号 | 任务 | 产出 |
|------|------|------|
| 1 | Docker Compose 一键部署 | `deploy/docker-compose.yml` + 5个 Dockerfile |
| 2 | Nginx 反向代理 | `deploy/nginx.conf` |
| 3 | 数据采集管道 | `data-pipeline/` 定时任务 |
| 4 | **四份文档主笔** | 需求规格/系统设计/测试报告/数据库文档 |
| 5 | 集成测试 | `tests/` 端到端测试 |
| 6 | GitHub 仓库管理 | Issue、分支保护、PR Review |

---

## 一、Docker Compose

### AI 服务 Dockerfile（李珈逾提供依赖清单）

```dockerfile
# deploy/ai-service.Dockerfile
FROM python:3.10-slim

WORKDIR /app

# 系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# Python 依赖
COPY ../ai-service/requirements.txt .
RUN pip install -r requirements.txt && \
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install sentence-transformers openai

COPY ../ai-service/ .

# 预加载模型（首次构建时下载，后续用缓存）
RUN python -c "from models.real_model import _load_model; _load_model(); print('ResNet50 OK')"

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: agri-mysql
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_PASSWORD:-agriculture2026}
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
    container_name: agri-redis
    ports:
      - "6379:6379"

  minio:
    image: minio/minio:latest
    container_name: agri-minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: admin
      MINIO_ROOT_PASSWORD: admin123456
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data

  ai-service:
    build:
      context: ..
      dockerfile: deploy/ai-service.Dockerfile
    container_name: agri-ai
    ports:
      - "8000:8000"
    environment:
      DEEPSEEK_API_KEY: ${DEEPSEEK_API_KEY}

  backend:
    build:
      context: ..
      dockerfile: deploy/backend.Dockerfile
    container_name: agri-backend
    ports:
      - "8080:8080"
    environment:
      SPRING_DATASOURCE_URL: jdbc:mysql://mysql:3306/agriculture?useUnicode=true&characterEncoding=utf-8&serverTimezone=Asia/Shanghai
      SPRING_DATASOURCE_USERNAME: root
      SPRING_DATASOURCE_PASSWORD: ${MYSQL_PASSWORD:-agriculture2026}
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
    container_name: agri-frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  mysql_data:
  minio_data:
```

### Nginx 配置

```nginx
server {
    listen 80;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://backend:8080/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 启动

```bash
cd deploy
docker compose up -d
docker compose ps          # 查看状态
docker compose logs -f     # 查看日志
```

---

## 二、数据采集管道

```
data-pipeline/
├── weather_collector.py
├── price_collector.py
├── bulletin_collector.py
└── scheduler.py
```

> 李珈逾的 AI 服务已经内置了天气/市场数据接口，你只需要写定时任务定期同步数据到莫成兴的数据库。或者更简单——前端直接调李珈逾的 `/api/weather` 和 `/api/market-prices`，你的数据管道只需要做一个定时缓存刷新。

## 三、四份文档

### 1. 需求规格说明书（10分）

**大纲：**
1. 项目背景 — 云南特色农业 + AI诊断痛点
2. 用户角色 — 农户/农技人员/合作社管理/管理员，各2-3条用户故事
3. 用例图 — Draw.io 画
4. 功能需求 — 按模块列，引用李珈逾的AI服务接口文档
5. 非功能需求 — 响应<3s, 图片<10MB, 支持6种作物

### 2. 系统设计说明书（10分）

**大纲：**
1. 架构图 — 前端(Nginx+Vue) → 后端(Spring Boot) → AI服务(FastAPI) → 数据库(MySQL)
2. ER图 — 用 `docs/数据库设计.md` 的表，Draw.io 画
3. 时序图 — 核心流程：用户上传图片 → 后端转发 → AI诊断(ResNet50+BERT+DeepSeek) → 返回结果
4. 部署图 — Docker Compose 各容器关系
5. 技术选型说明

> **李珈逾提供的技术栈描述（直接复制进系统设计文档）：**
> - 图像识别：PyTorch ResNet50 (ImageNet-1K预训练, 2048维特征向量, 余弦相似度匹配)
> - RAG检索：中文BERT Embedding (768维, 句向量, 余弦检索)
> - Agent推理：DeepSeek LLM + 规则引擎双模
> - 天气数据：Open-Meteo 免费全球天气API
> - 知识库：6份云南省农技规范文档

### 3. 测试报告（15分）

**李珈逾已完成的 AI 评测（直接放入测试报告）：**
- 见 `ai-service/tests/report.md`
- 端到端诊断：8/8 通过
- RAG检索可用率：7/8
- 平均响应时间：3ms
- 拒识测试：置信度 < 70% 标记人工审核

**你需要补充的：**
- 前端测试（找何志要 Vitest 截图）
- 后端测试（找莫成兴要 JUnit 截图）
- 接口测试（你用 Postman 测所有接口，导出报告）
- Docker 部署测试（docker compose up 截图）

### 4. 数据库设计文档

直接用 `docs/数据库设计.md` 和 `docs/schema.sql`。你负责：
- 加上 ER 图
- 补充索引说明
- 补充事务和迁移脚本说明

---

## 四、集成测试清单

```
1. docker compose up → 5个容器全部 Running ✅
2. http://localhost:8000/docs → AI服务 Swagger 页面 ✅
3. http://localhost:8080/api/auth/login → 后端登录 ✅
4. POST /api/diagnosis/upload → 上传图片返回 diagnosisId ✅
5. GET /api/diagnosis/{id} → 查询到 AI 诊断结果 ✅
6. http://localhost/ → 前端页面可访问 ✅
7. 登录 → 创建农场 → 创建地块 → 登记作物 → 上传诊断 → 查看结果 ✅
```

---

## 当前进度

| 模块 | 负责人 | 状态 |
|------|--------|------|
| AI 服务 | 李珈逾 | ✅ 已完成 |
| 数据库 SQL | 已有 | ✅ `docs/schema.sql` |
| 前端 6 页面 | 何志 | ❌ |
| 后端 Spring Boot | 莫成兴 | ❌ |
| 四份文档 | 陶柱宏 | ❌ |
| Docker 部署 | 陶柱宏 | ❌ |
| 集成测试 | 陶柱宏 | ❌ |
