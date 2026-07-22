# API 接口文档 v2.2

> ⚠️ **所有人开发的唯一真相源。改接口必须先更新本文档，再通知全组。**
>
> **李珈逾的 AI 服务已全部实现，以下是实际接口。莫成兴和何志直接对着这个写代码。**

## 基础信息

| 服务 | 地址 | 说明 |
|------|------|------|
| 业务后端 | `http://localhost:8080/api` | 莫成兴负责 |
| AI 服务 | `http://localhost:8000/api` | 李珈逾负责，已完成 |
| AI 文档页 | `http://localhost:8000/docs` | FastAPI 自动生成的 Swagger |

- **认证方式**：JWT Token，请求头 `Authorization: Bearer <token>`
- **响应格式**：JSON

### 统一响应结构（后端使用，AI服务直接返回数据）

```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

---

## 第一部分：AI 服务接口（李珈逾 → 莫成兴调用）

> 这些接口李珈逾已经实现并测试通过。莫成兴在 Spring Boot 中通过 RestTemplate/WebClient 调用。

### 1.1 健康检查

```
GET http://localhost:8000/api/health
```

**响应：**
```json
{
  "status": "ok",
  "version": "2.2.0",
  "model": "hsv_pixel_analysis",
  "rag": "tfidf_vector",
  "weather_api": "open_meteo",
  "crops_covered": ["番茄","辣椒","花卉","马铃薯","葡萄","茶叶"],
  "diseases_count": 35,
  "knowledge_entries": 29
}
```

### 1.2 病害诊断（核心）⭐

```
POST http://localhost:8000/api/diagnose
Content-Type: multipart/form-data
```

**输入参数：**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| image | File | 是 | 图片文件（JPG/PNG，≤10MB） |
| crop_type | String | 是 | 作物类型：番茄/辣椒/花卉/马铃薯/葡萄/茶叶 |
| growth_stage | String | 是 | 生育期：苗期/开花坐果期/结果期/成熟期/休眠期 |
| field_location | String | 是 | 地块位置，如：昆明呈贡、曲靖、玉溪、大理、红河等 |

**响应（实际格式，李珈逾返回的原始数据）：**
```json
{
  "disease": "番茄晚疫病",
  "confidence": 0.87,
  "symptoms": ["ResNet50特征匹配 (2048维)", "备选: 番茄早疫病, 番茄灰霉病"],
  "severity": "中等",
  "rag_result": {
    "summary": "霜脲·锰锌可湿性粉剂500倍液喷雾，配合通风降湿",
    "detail": "1. 立即摘除病叶、病果并集中深埋...",
    "source_title": "《云南省番茄主要病虫害防治技术规范》2024版",
    "source_section": "第三章 真菌性病害防治·第一节 晚疫病"
  },
  "agent_opinion": {
    "overall_assessment": "经综合研判，当前番茄（开花坐果期）感染了番茄晚疫病...",
    "risk_level": "high",
    "weather_factor": "当前气温24℃，湿度85%，阴转小雨。湿度偏高，利于病害发展。",
    "risk_factors": ["番茄晚疫病处于中等发展期，建议3天内采取措施", "作物处于开花坐果期，病害对产量影响较大"],
    "recommended_actions": [
      "【3日内】按防治方案处理番茄晚疫病：霜脲·锰锌可湿性粉剂500倍液喷雾...",
      "【辅助】通知农技人员确认诊断结果",
      "【辅助】处理后3-5天追拍照片复查，评估防治效果",
      "【参考】详见：《云南省番茄主要病虫害防治技术规范》2024版 第三章"
    ],
    "follow_up_days": 5
  }
}
```

**risk_level 取值**：`low` / `medium` / `high` / `critical`

**莫成兴调用示例（Java RestTemplate）：**
```java
MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
body.add("image", new ByteArrayResource(image.getBytes()) {
    @Override
    public String getFilename() { return image.getOriginalFilename(); }
});
body.add("crop_type", "番茄");
body.add("growth_stage", "开花坐果期");
body.add("field_location", "昆明呈贡");

HttpHeaders headers = new HttpHeaders();
headers.setContentType(MediaType.MULTIPART_FORM_DATA);

ResponseEntity<Map> response = restTemplate.postForEntity(
    "http://localhost:8000/api/diagnose",
    new HttpEntity<>(body, headers),
    Map.class
);
```

### 1.3 天气数据

```
GET http://localhost:8000/api/weather/{location}
```

**示例**：`GET /api/weather/昆明`

**响应：**
```json
{
  "location": "昆明",
  "temperature": 23.4,
  "humidity": 66,
  "rainfall": 0,
  "wind_speed": 2.5,
  "weather_desc": "晴",
  "risk_note": "湿度66%，干燥条件不利于多数病害",
  "forecast": [
    {"date": "2026-07-22", "temp_max": 26.0, "temp_min": 18.0, "precip": 0, "weather": "晴"},
    {"date": "2026-07-23", "temp_max": 24.7, "temp_min": 18.6, "precip": 5.2, "weather": "雷暴"}
  ],
  "source": "open-meteo"
}
```

### 1.4 市场价格

```
GET http://localhost:8000/api/market-prices?crop_type=番茄&days=30
```

**响应：**
```json
{
  "crop_type": "番茄",
  "summary": {
    "crop_type": "番茄",
    "latest_price": 3.8,
    "unit": "元/公斤",
    "week_average": 3.5,
    "trend": "上涨"
  },
  "records": [
    {"date": "2026-07-22", "price": 3.8, "unit": "元/公斤", "market": "呈贡龙城农贸市场"}
  ]
}
```

### 1.5 农业通报

```
GET http://localhost:8000/api/bulletins?crop_type=番茄&disease=晚疫病
```

**响应：**
```json
{
  "bulletins": [
    {
      "title": "云南省2026年7月农作物病虫发生趋势预报",
      "source": "云南省农业农村厅",
      "date": "2026-07-01",
      "summary": "预计7月份番茄晚疫病在昆明、曲靖、玉溪等主产区中等偏重发生...",
      "risk_level": "high",
      "relevant_crops": ["番茄", "辣椒", "马铃薯"]
    }
  ]
}
```

---

## 第二部分：后端接口（莫成兴 → 何志调用）

> Spring Boot，端口 8080。莫成兴负责实现。

### 2.1 认证

#### 注册
```
POST /api/auth/register
Body: { "username": "farmer1", "password": "123456", "realName": "张三", "phone": "13800138000", "role": "farmer" }
Response: { "code": 200, "data": { "userId": 1, "username": "farmer1" } }
```

#### 登录
```
POST /api/auth/login
Body: { "username": "farmer1", "password": "123456" }
Response: { "code": 200, "data": { "token": "eyJ...", "user": { "id":1, "username":"farmer1", "role":"farmer" } } }
```

> 后续所有接口请求头带 `Authorization: Bearer {token}`

### 2.2 农场与地块

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/farms` | 农场列表 |
| POST | `/api/farms` | 创建农场 `{name, address, description}` |
| GET | `/api/fields?farmId=1` | 地块列表 |
| POST | `/api/fields` | 创建地块 `{farmId, name, area, soilType, locationDesc}` |
| GET | `/api/fields/{id}` | 地块详情（含当前作物） |

### 2.3 作物

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/crops?fieldId=1` | 作物列表 |
| POST | `/api/crops` | 登记作物 `{fieldId, cropType, variety, plantDate}` |
| PUT | `/api/crops/{id}` | 更新状态 `{growthStage, status}` |

### 2.4 病害诊断（莫成兴转发到李珈逾的AI服务）⭐

```
POST /api/diagnosis/upload
Content-Type: multipart/form-data
参数: image(File), fieldId(Long), cropId(Long), description(String,可选)
```

**莫成兴的实现逻辑：**
```
1. 接收图片 → 存到 MinIO
2. 创建 observation 记录
3. 创建 diagnosis_record（status=processing）
4. 异步调用李珈逾的 AI 服务: POST http://localhost:8000/api/diagnose
5. 拿到结果 → 更新 diagnosis_record（status=completed）
6. 返回 diagnosisId 给前端
```

**查询结果：**
```
GET /api/diagnosis/{id}
Response: 包含 AI 服务返回的全部字段 + 审核状态
```

**诊断列表：**
```
GET /api/diagnosis/list?fieldId=1&status=completed&page=1&size=20
```

**农技人员审核：**
```
PUT /api/diagnosis/{id}/review
Body: { "action": "approve", "comment": "诊断准确" }
```

### 2.5 农事任务

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tasks?fieldId=1&status=pending` | 任务列表 |
| POST | `/api/tasks` | 创建任务 `{fieldId, cropId, taskType, description, dueDate}` |
| PUT | `/api/tasks/{id}/status` | 更新状态 `{status: "completed"}` |

> taskType: spray(喷药) / fertilize(施肥) / irrigate(灌溉) / prune(修剪) / harvest(收获) / other

### 2.6 数据看板

```
GET /api/weather?location=昆明呈贡&days=7
→ 转发到 AI 服务 GET http://localhost:8000/api/weather/昆明呈贡

GET /api/market-prices?cropType=番茄&days=30
→ 转发到 AI 服务 GET http://localhost:8000/api/market-prices?crop_type=番茄&days=30
```

---

## 第三部分：对接清单

### 何志（前端）需要调的接口

| 页面 | 方法 + 路径 |
|------|-----------|
| 登录 | POST `/api/auth/login` |
| 注册 | POST `/api/auth/register` |
| 农场管理 | GET/POST `/api/farms` |
| 地块管理 | GET/POST `/api/fields`, GET `/api/fields/{id}` |
| 作物档案 | GET/POST `/api/crops`, PUT `/api/crops/{id}` |
| **病害诊断** | POST `/api/diagnosis/upload` → 轮询 GET `/api/diagnosis/{id}` |
| 诊断历史 | GET `/api/diagnosis/list` |
| 农事日历 | GET/POST `/api/tasks`, PUT `/api/tasks/{id}/status` |
| 数据看板 | GET `/api/weather?location=...`, GET `/api/market-prices?cropType=...` |

### 莫成兴（后端）需要调的接口

| 场景 | 地址 |
|------|------|
| AI病害诊断 | POST `http://localhost:8000/api/diagnose` |
| AI服务健康检查 | GET `http://localhost:8000/api/health` |
| 天气数据 | GET `http://localhost:8000/api/weather/{location}` |
| 市场价格 | GET `http://localhost:8000/api/market-prices?crop_type=XX` |

### 李珈逾（AI服务）启动命令

```bash
cd ai-service
venv\Scripts\activate
set DEEPSEEK_API_KEY=你的DeepSeek密钥
uvicorn main:app --reload --port 8000
```
