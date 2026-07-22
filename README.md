# 云南特色农业智能诊断与生产管理平台

> 期末大作业 · 选题三 · 四人小组
>
> 仓库地址：`git@github.com:4JOKERKING/88888888.git`

## 技术栈

| 层次 | 技术 |
|------|------|
| 前端 | Vue 3 + TypeScript + Vite + Pinia + Element Plus + ECharts |
| 业务后端 | Spring Boot + MyBatis-Plus + MySQL |
| AI 服务 | Python + FastAPI + LangChain + ChromaDB |
| 文件存储 | MinIO（图片） |
| 缓存/队列 | Redis + Celery |
| 部署 | Docker Compose + Nginx |

## 团队分工

| 成员 | GitHub 分支 | 负责模块 | 核心任务 |
|------|------------|---------|---------|
| **何志** | `feature/frontend` | 前端 | Vue 3 全部页面 + ECharts + 图片上传 |
| **莫成兴** | `feature/backend` | 后端 | Spring Boot API + 数据库 + RBAC + 调用 AI |
| **李珈逾** | `feature/ai-service` | AI 服务 | FastAPI + 图像识别 + RAG + Agent 编排 |
| **陶柱宏** | `feature/deploy-docs` | 部署+文档 | Docker + 数据管道 + 四份文档主笔 + 测试 |

## 项目结构

```
project/
├── frontend/          # 何志：Vue 3 前端
├── backend/           # 莫成兴：Spring Boot 后端
├── ai-service/        # 李珈逾：Python FastAPI AI 服务
├── data-pipeline/     # 陶柱宏：数据采集定时任务
├── deploy/            # 陶柱宏：Docker Compose + Nginx 配置
├── docs/              # 全员 + 陶柱宏统筹
│   ├── API接口文档.md        # ← 最重要的对接文档
│   ├── 数据库设计.md          # 莫成兴维护
│   ├── schema.sql            # 建表 SQL
│   ├── 环境搭建指南.md        # 每人配环境看这个
│   └── 各人开发指南/          # 每人一份
├── tests/             # 陶柱宏：集成测试
└── README.md
```

---

## ⚠️ 协作铁律（所有人必读）

### 1. 接口即合同

[`docs/API接口文档.md`](docs/API接口文档.md) 是唯一真相源。

- **任何人修改接口，必须在群里通知另外三人**
- 何志只调文档里的接口，莫成兴只实现文档里的接口
- 李珈逾只提供文档里定义的 AI 服务接口
- 如果发现文档里缺了什么，先更新文档，再写代码

### 2. Git 分支规范

```bash
main                    # 只放能跑通的代码
feature/frontend        # 何志
feature/backend         # 莫成兴
feature/ai-service      # 李珈逾
feature/deploy-docs     # 陶柱宏
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

### 3. 代码格式规范

> ⚠️ 都用 AI 写代码，不加规范的话四个人风格打架，合并时全是冲突。

**通用规则（.editorconfig 已配置，自动生效）：**
- 缩进：前端用 2 空格，Java/Python 用 4 空格
- 编码：UTF-8
- 换行：LF
- 行尾去空格

**Git Commit 格式：**
```bash
feat: 添加病害图片上传组件       # 新功能
fix: 修复诊断结果轮询超时问题     # 修bug
docs: 更新接口文档               # 文档改动
refactor: 重构图片识别模块       # 重构
```

**前端（何志）：**
- 组件名用 PascalCase：`DiagnosisUpload.vue`
- 文件名用小写+连字符：`api/diagnosis.js`
- 用 Element Plus 组件，自己尽量少写原生 CSS

**后端（莫成兴）：**
- 类名 PascalCase：`DiagnosisController`
- 方法名 camelCase：`getDiagnosisById()`
- URL 用小写+连字符：`/api/diagnosis/upload`
- 数据库字段用下划线：`diagnosis_records`

**Python（李珈逾、陶柱宏）：**
- 文件名小写+下划线：`image_model.py`
- 函数名小写+下划线：`recognize_disease()`
- 类名 PascalCase：`DiagnosisAgent`

**通用—AI 生成代码后必做：**
1. 删掉 AI 的废话注释
2. 删掉没用的 import
3. 格式化一下（VS Code: `Shift+Alt+F`）

### 4. 每天 10 分钟同步

在群里简短汇报三句话：
1. 今天完成了什么
2. 卡在哪里了
3. 有没有改接口

### 5. 当前进度

| 模块 | 负责人 | 状态 |
|------|--------|------|
| AI 服务（ResNet50+BERT+DeepSeek） | 李珈逾 | ✅ 已完成 |
| 数据库设计 + SQL | 已交付 | ✅ `docs/schema.sql` |
| API 接口文档 | 已交付 | ✅ `docs/API接口文档.md` |
| 前端 6 页面 | 何志 | ❌ 待启动 |
| 后端 Spring Boot | 莫成兴 | ❌ 待启动 |
| 四份文档 | 陶柱宏 | ❌ 待启动 |
| Docker 部署 | 陶柱宏 | ❌ 待确认 |

### 6. .gitignore 已配好

不要提交 `node_modules/`、`target/`、`__pycache__/`、`venv/`、`.env` 等。

---

## 开发顺序（按这个来）

| 阶段 | 做什么 | 谁来做 |
|------|--------|--------|
| **第1步** | 读完全部指导文档，配好开发环境 | 全员 |
| **第2步** | 莫成兴建好数据库，陶柱宏确认 Docker | 莫成兴 + 陶柱宏 |
| **第3步** | 李珈逾把 AI 服务跑起来（先实现最简单的图片识别） | 李珈逾 |
| **第4步** | 莫成兴实现基础 CRUD API（地块、作物） | 莫成兴 |
| **第5步** | 莫成兴对接李珈逾的 AI 服务，实现诊断接口 | 莫成兴 + 李珈逾 |
| **第6步** | 何志开始写前端页面（对着 API 文档） | 何志 |
| **第7步** | 陶柱宏写数据采集管道 + 完善文档 | 陶柱宏 |
| **第8步** | 前后端联调 | 何志 + 莫成兴 |
| **第9步** | 陶柱宏用 Docker Compose 部署全套 | 陶柱宏 |
| **第10步** | 端到端测试 + 准备答辩 | 全员 |

---

## 评分维度对应

| 评分维度 | 分值 | 负责人 |
|---------|------|--------|
| 需求分析与系统设计 | 10 | 陶柱宏（主笔） |
| 前端功能和交互质量 | 10 | 何志 |
| 后端业务逻辑与数据库 | 20 | 莫成兴 |
| RAG、Agent、微调与评测 | 25 | 李珈逾（核心）+ 陶柱宏（RAG/Agent） |
| 测试、部署、性能与可维护性 | 15 | 陶柱宏 |
| 数据合规、安全与审计 | 10 | 莫成兴（RBAC）+ 陶柱宏（文档） |
| 团队协作和答辩 | 10 | 全员 |

---

## 下一步

→ 打开 [`docs/环境搭建指南.md`](docs/环境搭建指南.md) 安装开发环境
→ 打开 [`docs/API接口文档.md`](docs/API接口文档.md) 了解所有接口
→ 打开 `docs/各人开发指南/` 目录下你的那份指南
