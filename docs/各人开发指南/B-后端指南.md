# 莫成兴 — 后端开发指南（Spring Boot）

> ⚠️ **李珈逾的 AI 服务已经写完并测试通过。你直接调她的接口，不需要自己实现 AI。**

## 你需要做的事

| 序号 | 模块 | 接口数 | 难度 |
|------|------|--------|------|
| 1 | 认证（登录/注册/JWT） | 3 | ⭐⭐ |
| 2 | 农场/地块 CRUD | 5 | ⭐ |
| 3 | 作物 CRUD | 3 | ⭐ |
| 4 | **病害诊断（转发AI服务）** | 4 | ⭐⭐⭐ |
| 5 | 农事任务 CRUD | 3 | ⭐ |
| 6 | 数据看板（转发天气/价格） | 2 | ⭐ |
| 7 | RBAC 权限控制 | 1 | ⭐⭐ |

## 项目结构

```
backend/
├── src/main/java/com/agriculture/
│   ├── controller/      # HTTP 接口层
│   ├── service/         # 业务逻辑层
│   ├── mapper/          # MyBatis-Plus 数据库
│   ├── entity/          # 实体类
│   ├── dto/             # 请求/响应对象
│   ├── config/          # Security/CORS 配置
│   └── common/          # JWT工具/统一响应
├── src/main/resources/
│   ├── application.yml
│   └── mapper/
└── pom.xml
```

## 重点：调用李珈逾的 AI 服务

李珈逾的服务跑在 `http://localhost:8000`。你需要在这里调她：

### 诊断接口（核心）

```java
// DiagnosisService.java
@Service
public class DiagnosisService {

    private final RestTemplate restTemplate = new RestTemplate();

    @Async  // 异步执行，不阻塞主线程
    public void callAiService(Long diagnosisId, byte[] imageBytes,
                               String filename, String cropType,
                               String growthStage, String location) {
        // 1. 构建请求
        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("image", new ByteArrayResource(imageBytes) {
            @Override
            public String getFilename() { return filename; }
        });
        body.add("crop_type", cropType);
        body.add("growth_stage", growthStage);
        body.add("field_location", location);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        // 2. 调用李珈逾的 AI 服务
        String aiUrl = "http://localhost:8000/api/diagnose";
        ResponseEntity<Map> response = restTemplate.postForEntity(
            aiUrl,
            new HttpEntity<>(body, headers),
            Map.class
        );

        // 3. 把结果写回数据库
        Map<String, Object> result = response.getBody();
        updateDiagnosisRecord(diagnosisId, result);
    }

    private void updateDiagnosisRecord(Long id, Map<String, Object> aiResult) {
        DiagnosisRecord record = diagnosisMapper.selectById(id);
        record.setDisease((String) aiResult.get("disease"));
        record.setConfidence(BigDecimal.valueOf((Double) aiResult.get("confidence")));
        record.setRecognitionResult(JSON.toJSONString(aiResult));
        record.setRagSuggestion(JSON.toJSONString(aiResult.get("rag_result")));
        record.setAgentOpinion(JSON.toJSONString(aiResult.get("agent_opinion")));
        record.setRiskLevel((String) ((Map)aiResult.get("agent_opinion")).get("risk_level"));
        record.setStatus("completed");
        diagnosisMapper.updateById(record);
    }
}
```

### 诊断上传接口

```java
@RestController
@RequestMapping("/api/diagnosis")
public class DiagnosisController {

    @PostMapping("/upload")
    public Result<Map> upload(
            @RequestParam MultipartFile image,
            @RequestParam Long fieldId,
            @RequestParam Long cropId,
            @RequestParam(required = false) String description) {

        // 1. 校验（≤10MB, JPG/PNG）
        if (image.getSize() > 10 * 1024 * 1024) {
            return Result.error(400, "图片不能超过10MB");
        }

        // 2. 存图片到 MinIO（MinIO未配好时先存本地）
        String imageUrl = fileService.upload(image);

        // 3. 查作物信息
        Crop crop = cropMapper.selectById(cropId);

        // 4. 创建诊断记录（status=processing）
        DiagnosisRecord record = new DiagnosisRecord();
        record.setFieldId(fieldId);
        record.setCropId(cropId);
        record.setImageUrl(imageUrl);
        record.setStatus("processing");
        diagnosisMapper.insert(record);

        // 5. 异步调用李珈逾的AI服务
        diagnosisService.callAiService(
            record.getId(),
            image.getBytes(),
            image.getOriginalFilename(),
            crop.getCropType(),     // 如 "番茄"
            crop.getGrowthStage(),  // 如 "开花坐果期"
            getLocation(fieldId)    // 如 "昆明呈贡"
        );

        // 6. 立即返回 diagnosisId
        Map<String, Object> data = new HashMap<>();
        data.put("diagnosisId", record.getId());
        data.put("status", "processing");
        return Result.ok(data);
    }

    @GetMapping("/{id}")
    public Result<DiagnosisRecord> getResult(@PathVariable Long id) {
        DiagnosisRecord record = diagnosisMapper.selectById(id);
        return Result.ok(record);
    }

    @GetMapping("/list")
    public Result<PageResult> list(
            @RequestParam(required = false) Long fieldId,
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size) {
        Page<DiagnosisRecord> result = diagnosisService.listByPage(fieldId, status, page, size);
        return Result.ok(result);
    }
}
```

### 天气和价格——转发到李珈逾的AI服务

```java
@GetMapping("/api/weather")
public Result<?> getWeather(@RequestParam String location) {
    // 直接转发到李珈逾的服务
    String url = "http://localhost:8000/api/weather/" + location;
    Map<String, Object> data = restTemplate.getForObject(url, Map.class);
    return Result.ok(data);
}

@GetMapping("/api/market-prices")
public Result<?> getMarketPrices(@RequestParam String cropType) {
    String url = "http://localhost:8000/api/market-prices?crop_type=" + cropType;
    Map<String, Object> data = restTemplate.getForObject(url, Map.class);
    return Result.ok(data);
}
```

## application.yml

```yaml
server:
  port: 8080

spring:
  datasource:
    url: jdbc:mysql://localhost:3306/agriculture?useUnicode=true&characterEncoding=utf-8&serverTimezone=Asia/Shanghai
    username: root
    password: 你的密码
    driver-class-name: com.mysql.cj.jdbc.Driver

  servlet:
    multipart:
      max-file-size: 10MB

mybatis-plus:
  configuration:
    map-underscore-to-camel-case: true
  global-config:
    db-config:
      id-type: auto
```

## 数据库初始化

```bash
mysql -u root -p < docs/schema.sql
```

## 调试

1. 先确认李珈逾的服务已启动：浏览器打开 `http://localhost:8000/docs`
2. 用 Postman 测试自己写的接口
3. 数据库可视化：Navicat 或 DBeaver 连 MySQL
