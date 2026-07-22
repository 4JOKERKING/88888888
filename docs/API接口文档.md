# API 接口文档 v1.0

> ⚠️ **这是所有人开发的唯一真相源。改接口必须先更新本文档，再通知全组。**

## 基础信息

- **Base URL**：`http://localhost:8080/api`
- **AI 服务 Base URL**：`http://localhost:8000/api`
- **认证方式**：JWT Token，请求头 `Authorization: Bearer <token>`
- **请求格式**：JSON（除文件上传用 `multipart/form-data`）
- **响应格式**：JSON

### 统一响应结构

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

### 统一错误码

| code | 含义 |
|------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未登录或 Token 过期 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 一、认证模块（Auth）

### 1.1 注册

```
POST /api/auth/register
```

**请求体：**
```json
{
  "username": "zhangsan",
  "password": "123456",
  "realName": "张三",
  "phone": "13800138000",
  "role": "farmer"
}
```

> role 可选值：`farmer`（农户）、`technician`（农技人员）、`manager`（合作社管理）、`admin`（管理员）

**响应：**
```json
{
  "code": 200,
  "message": "注册成功",
  "data": {
    "userId": 1,
    "username": "zhangsan"
  }
}
```

### 1.2 登录

```
POST /api/auth/login
```

**请求体：**
```json
{
  "username": "zhangsan",
  "password": "123456"
}
```

**响应：**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
      "id": 1,
      "username": "zhangsan",
      "realName": "张三",
      "role": "farmer"
    }
  }
}
```

### 1.3 获取当前用户

```
GET /api/auth/me
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "username": "zhangsan",
    "realName": "张三",
    "role": "farmer",
    "phone": "13800138000"
  }
}
```

---

## 二、农场与地块模块（Farm & Field）

### 2.1 创建农场

```
POST /api/farms
```

**请求体：**
```json
{
  "name": "阳光农场",
  "address": "云南省昆明市呈贡区",
  "description": "主要种植蔬菜和花卉"
}
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "name": "阳光农场",
    "address": "云南省昆明市呈贡区"
  }
}
```

### 2.2 农场列表

```
GET /api/farms
```

**响应：**
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "阳光农场",
      "address": "云南省昆明市呈贡区",
      "fieldCount": 3
    }
  ]
}
```

### 2.3 创建地块

```
POST /api/fields
```

**请求体：**
```json
{
  "farmId": 1,
  "name": "A区-1号地",
  "area": 2.5,
  "areaUnit": "亩",
  "soilType": "红壤",
  "locationDesc": "农场东侧靠河"
}
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "farmId": 1,
    "name": "A区-1号地",
    "area": 2.5
  }
}
```

### 2.4 地块列表

```
GET /api/fields?farmId=1
```

**响应：**
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "farmId": 1,
      "name": "A区-1号地",
      "area": 2.5,
      "areaUnit": "亩",
      "soilType": "红壤",
      "currentCrop": "番茄"
    }
  ]
}
```

### 2.5 地块详情

```
GET /api/fields/{id}
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "farmId": 1,
    "farmName": "阳光农场",
    "name": "A区-1号地",
    "area": 2.5,
    "areaUnit": "亩",
    "soilType": "红壤",
    "locationDesc": "农场东侧靠河",
    "crops": [
      {
        "id": 1,
        "cropType": "番茄",
        "variety": "粉果1号",
        "plantDate": "2026-03-15",
        "growthStage": "开花坐果期",
        "status": "growing"
      }
    ]
  }
}
```

---

## 三、作物模块（Crop）

### 3.1 登记作物

```
POST /api/crops
```

**请求体：**
```json
{
  "fieldId": 1,
  "cropType": "番茄",
  "variety": "粉果1号",
  "plantDate": "2026-03-15",
  "plantArea": 1.5,
  "areaUnit": "亩",
  "notes": "大棚种植"
}
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "fieldId": 1,
    "cropType": "番茄",
    "variety": "粉果1号",
    "plantDate": "2026-03-15",
    "growthStage": "苗期",
    "status": "growing"
  }
}
```

### 3.2 作物列表

```
GET /api/crops?fieldId=1
```

### 3.3 更新作物状态

```
PUT /api/crops/{id}
```

**请求体：**
```json
{
  "growthStage": "开花坐果期",
  "status": "growing",
  "notes": "长势良好"
}
```

---

## 四、病害诊断模块（核心 Diagnosis）⭐

这是本项目的核心功能。流程：
```
用户上传图片 → 后端保存图片到 MinIO → 后端调用 AI 服务 → 
AI 进行图像识别 + RAG 检索农技规范 + Agent 综合研判 → 
返回结果给后端 → 后端入库 → 前端展示
```

### 4.1 上传图片发起诊断

```
POST /api/diagnosis/upload
Content-Type: multipart/form-data
```

**表单参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| image | File | 是 | 病害图片（jpg/png，≤10MB） |
| fieldId | Integer | 是 | 地块ID |
| cropId | Integer | 是 | 作物ID |
| description | String | 否 | 症状文字描述 |

**响应（异步，立即返回诊断ID）：**
```json
{
  "code": 200,
  "message": "图片已提交，正在识别中",
  "data": {
    "diagnosisId": 42,
    "status": "processing"
  }
}
```

### 4.2 查询诊断结果

```
GET /api/diagnosis/{id}
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "id": 42,
    "status": "completed",
    "imageUrl": "http://localhost:9000/agriculture/diagnosis/2026/07/xxx.jpg",
    "cropType": "番茄",
    "growthStage": "开花坐果期",
    "recognitionResult": {
      "disease": "番茄晚疫病",
      "confidence": 0.92,
      "symptoms": ["叶片出现水渍状斑点", "叶背有白色霉层"],
      "severity": "中等"
    },
    "ragSuggestion": {
      "summary": "建议使用霜脲·锰锌可湿性粉剂500倍液喷雾防治",
      "detail": "1. 立即摘除病叶并集中深埋\n2. 喷洒霜脲·锰锌可湿性粉剂500倍液，每7天一次，连续2-3次\n3. 加强通风降湿，控制大棚内湿度在70%以下\n4. 增施磷钾肥，提高植株抗病能力",
      "sourceDocument": "《云南省番茄主要病虫害防治技术规范》2024版",
      "sourceSection": "第三章 真菌性病害防治"
    },
    "agentOpinion": {
      "overallAssessment": "综合当前天气（多雨高湿）、作物生育期（开花坐果期）和识别结果，判断为番茄晚疫病中期，需尽快处理。该病害在高湿环境下传播迅速，3-5天内可感染整棚。",
      "riskLevel": "high",
      "weatherFactor": "近期连续阴雨，空气湿度85%，利于晚疫病扩散",
      "recommendedActions": [
        "优先：立即药剂防治，霜脲·锰锌500倍液喷雾",
        "辅助：摘除病叶、加强通风",
        "长期：调整种植密度，选用抗病品种"
      ],
      "followUpDays": 7
    },
    "reviewedBy": null,
    "createdAt": "2026-07-22T14:30:00"
  }
}
```

> status 取值：`processing`（识别中）、`completed`（已完成）、`reviewed`（已审核）、`rejected`（需重新识别）

### 4.3 诊断记录列表

```
GET /api/diagnosis/list?fieldId=1&status=completed&page=1&size=20
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "total": 15,
    "page": 1,
    "records": [
      {
        "id": 42,
        "cropType": "番茄",
        "disease": "番茄晚疫病",
        "riskLevel": "high",
        "status": "completed",
        "createdAt": "2026-07-22T14:30:00"
      }
    ]
  }
}
```

### 4.4 农技人员审核诊断结果

```
PUT /api/diagnosis/{id}/review
```

**请求体：**
```json
{
  "action": "approve",
  "comment": "诊断结果准确，建议可行"
}
```

> action 取值：`approve`（通过）、`revise`（建议修改）

---

## 五、农事任务模块（Task）

### 5.1 任务列表

```
GET /api/tasks?fieldId=1&status=pending&page=1&size=20
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "total": 8,
    "records": [
      {
        "id": 1,
        "fieldId": 1,
        "cropType": "番茄",
        "taskType": "spray",
        "description": "喷洒霜脲·锰锌500倍液防治晚疫病",
        "dueDate": "2026-07-24",
        "status": "pending",
        "assignedTo": "张三",
        "sourceDiagnosisId": 42
      }
    ]
  }
}
```

> taskType 取值：`spray`（喷药）、`fertilize`（施肥）、`irrigate`（灌溉）、`prune`（修剪）、`harvest`（收获）、`other`（其他）

### 5.2 创建任务

```
POST /api/tasks
```

**请求体：**
```json
{
  "fieldId": 1,
  "cropId": 1,
  "taskType": "spray",
  "description": "喷洒霜脲·锰锌500倍液防治晚疫病",
  "dueDate": "2026-07-24",
  "assignedTo": "张三",
  "sourceDiagnosisId": 42
}
```

### 5.3 更新任务状态

```
PUT /api/tasks/{id}/status
```

**请求体：**
```json
{
  "status": "completed",
  "notes": "已喷洒，植株情况稳定"
}
```

> status 取值：`pending`、`in_progress`、`completed`、`cancelled`

---

## 六、数据看板模块（Dashboard）

### 6.1 天气数据

```
GET /api/weather?location=昆明呈贡&days=7
```

**响应：**
```json
{
  "code": 200,
  "data": [
    {
      "date": "2026-07-22",
      "temperature": 24.5,
      "humidity": 85,
      "rainfall": 12.3,
      "weatherDesc": "小雨转阴",
      "windSpeed": 2.5
    }
  ]
}
```

### 6.2 市场价格

```
GET /api/market-prices?cropType=番茄&days=30
```

**响应：**
```json
{
  "code": 200,
  "data": [
    {
      "date": "2026-07-22",
      "cropType": "番茄",
      "price": 3.5,
      "unit": "元/公斤",
      "market": "呈贡龙城农贸市场"
    }
  ]
}
```

---

## 七、模型监控模块（Model Monitor）

### 7.1 模型性能指标

```
GET /api/model/performance
```

**响应：**
```json
{
  "code": 200,
  "data": {
    "imageModel": {
      "name": "plant-disease-resnet50-v2",
      "version": "2.1.0",
      "accuracy": 0.91,
      "totalPredictions": 1560,
      "rejectionRate": 0.08,
      "lastDeployed": "2026-07-15"
    },
    "unknownSamples": 23
  }
}
```

---

## 八、AI 服务内部接口（后端 ↔ AI 服务）

> 这些接口由 **C 实现**，**B 调用**。前端不直接调 AI 服务。

### 8.1 图像识别

```
POST http://localhost:8000/api/diagnose
Content-Type: multipart/form-data
```

**参数：**

| 参数 | 类型 | 说明 |
|------|------|------|
| image | File | 图片文件 |
| crop_type | String | 作物类型 |
| growth_stage | String | 生育期 |
| field_location | String | 地块位置（用于获取天气） |

**响应：**
```json
{
  "disease": "番茄晚疫病",
  "confidence": 0.92,
  "symptoms": ["叶片出现水渍状斑点", "叶背有白色霉层"],
  "severity": "中等",
  "rag_result": {
    "summary": "建议使用霜脲·锰锌...",
    "detail": "1. 立即摘除病叶...",
    "source_title": "《云南省番茄主要病虫害防治技术规范》",
    "source_section": "第三章"
  },
  "agent_opinion": {
    "overall_assessment": "综合天气、生育期...",
    "risk_level": "high",
    "weather_factor": "近期连续阴雨...",
    "recommended_actions": ["优先：立即药剂防治", "辅助：摘除病叶"],
    "follow_up_days": 7
  }
}
```

### 8.2 健康检查

```
GET http://localhost:8000/api/health
```

**响应：**
```json
{
  "status": "ok",
  "model_loaded": true,
  "model_version": "2.1.0"
}
```

---

## 🔄 A（前端）调用清单

| 页面 | 调用的接口 |
|------|-----------|
| 登录/注册 | POST /api/auth/login, POST /api/auth/register |
| 农场管理 | GET/POST /api/farms |
| 地块管理 | GET/POST /api/fields, GET /api/fields/{id} |
| 作物档案 | GET/POST /api/crops, PUT /api/crops/{id} |
| 病害诊断页 | POST /api/diagnosis/upload, GET /api/diagnosis/{id} |
| 诊断历史 | GET /api/diagnosis/list |
| 农事日历 | GET/POST /api/tasks, PUT /api/tasks/{id}/status |
| 数据看板 | GET /api/weather, GET /api/market-prices |
| 模型监控 | GET /api/model/performance |

## 🔄 B（后端）调用 C（AI 服务）清单

| 场景 | 调用的接口 |
|------|-----------|
| 收到诊断请求时 | POST http://localhost:8000/api/diagnose |
| 服务启动检查 | GET http://localhost:8000/api/health |
