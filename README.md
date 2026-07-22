# 云南特色农业智能诊断与生产管理平台

> 期末大作业 · 选题三 · 四人小组

## 技术栈

| 层次 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Vite + Pinia + Element Plus + ECharts |
| 业务后端 | Spring Boot + MyBatis-Plus + MySQL |
| AI 服务 | Python + FastAPI + LangChain |
| 文件存储 | MinIO（图片） |
| 缓存/队列 | Redis + Celery |
| 部署 | Docker Compose + Nginx |

## 团队分工

| 成员 | 负责模块 | 核心任务 | 产出文件 |
|------|---------|---------|---------|
| **A** | 前端 | 全部页面 + ECharts 图表 + 图片上传组件 | `frontend/` |
| **B** | 后端 | Spring Boot API + 数据库 + RBAC 权限 + 调用 AI 服务 | `backend/` |
| **C** | AI 服务 | FastAPI + 图像识别 + RAG 检索 + Agent 编排 | `ai-service/` |
| **D** | 部署 + 文档 | Docker Compose + 数据管道 + 四份文档主笔 + 集成测试 | `deploy/` `docs/` `tests/` |

## 项目结构

```
project/
├── frontend/          # A 负责：Vue 3 前端
├── backend/           # B 负责：Spring Boot 后端
├── ai-service/        # C 负责：Python FastAPI AI 服务
├── data-pipeline/     # D 负责：数据采集定时任务
├── deploy/            # D 负责：Docker Compose + Nginx 配置
├── docs/              # 全员 + D 统筹：所有文档
│   ├── API接口文档.md        # ← 最重要的对接文档，所有人对着它开发
│   ├── 数据库设计.md          # B 维护，C/D 参考
│   ├── 环境搭建指南.md        # 每人配环境看这个
│   └── 各人开发指南/          # 每人一份详细步骤
├── tests/             # D 负责：集成测试
└── README.md          # 本文件
```

---

## ⚠️ 协作铁律（所有人必读）

### 1. 接口即合同

[`docs/API接口文档.md`](docs/API接口文档.md) 是唯一真相源。

- **任何人修改接口，必须在群里通知另外三人**
- 前端 A 只调文档里的接口，后端 B 只实现文档里的接口
- 如果发现文档里缺了什么，先更新文档，再写代码

### 2. Git 分支规范

```bash
main                    # 只放能跑通的代码
feature/frontend        # A 的分支
feature/backend         # B 的分支
feature/ai-service      # C 的分支
feature/deploy-docs     # D 的分支
```

**每天流程：**
```bash
git add .
git commit -m "feat: 完成了xxx功能"
git push origin feature/你的分支
```

**绝对禁止：**
- ❌ 直接在 main 分支上改代码
- ❌ `git push --force`（强制推送）
- ❌ 把 node_modules/、target/、__pycache__/ 提交到仓库
- ❌ 修改别人的文件不打招呼

### 3. 每天 10 分钟同步

在群里简短汇报三句话：
1. 今天完成了什么
2. 卡在哪里了
3. 有没有改接口

### 4. .gitignore 必须包含

```
node_modules/
target/
__pycache__/
*.pyc
.env
.idea/
.vscode/
dist/
*.log
uploads/
```

---

## 开发顺序（按这个来）

| 阶段 | 做什么 | 谁来做 |
|------|--------|--------|
| **第1步** | 读完全部指导文档，配好开发环境 | 全员 |
| **第2步** | B 建好数据库，D 跑通 Docker | B + D |
| **第3步** | C 把 AI 服务跑起来（先实现最简单的图片识别） | C |
| **第4步** | B 实现基础 CRUD API（地块、作物） | B |
| **第5步** | B 对接 C 的 AI 服务，实现诊断接口 | B + C |
| **第6步** | A 开始写前端页面（对着 API 文档） | A |
| **第7步** | D 写数据采集管道 + 完善文档 | D |
| **第8步** | 前后端联调 | A + B |
| **第9步** | D 用 Docker Compose 部署全套 | D |
| **第10步** | 端到端测试 + 准备答辩 | 全员 |

---

## 评分维度对应

| 评分维度 | 分值 | 负责人 |
|---------|------|--------|
| 需求分析与系统设计 | 10 | D（主笔） |
| 前端功能和交互质量 | 10 | A |
| 后端业务逻辑与数据库 | 20 | B |
| RAG、Agent、微调与评测 | 25 | C（核心）+ D（RAG/Agent） |
| 测试、部署、性能与可维护性 | 15 | D |
| 数据合规、安全与审计 | 10 | B（RBAC）+ D（文档） |
| 团队协作和答辩 | 10 | 全员 |

---

## 下一步

→ 打开 [`docs/环境搭建指南.md`](docs/环境搭建指南.md) 安装开发环境
→ 打开 [`docs/API接口文档.md`](docs/API接口文档.md) 了解所有接口
→ 打开 `docs/各人开发指南/` 目录下你的那份指南
