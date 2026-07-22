# 莫成兴 — 后端开发指南（Spring Boot）

> 你的任务：实现全部 API + 数据库设计 + RBAC 权限 + 调用李珈逾的 AI 服务。

## 你需要做的事

### API 清单（按开发顺序）

| 序号 | 模块 | 接口数 | 难度 |
|------|------|--------|------|
| 1 | 认证（登录/注册/JWT） | 3 | ⭐⭐ |
| 2 | 农场/地块 CRUD | 5 | ⭐ |
| 3 | 作物 CRUD | 3 | ⭐ |
| 4 | **病害诊断**（核心） | 4 | ⭐⭐⭐ |
| 5 | 农事任务 CRUD | 3 | ⭐ |
| 6 | 数据看板（天气/价格） | 2 | ⭐ |
| 7 | 模型监控 | 1 | ⭐ |

### 项目结构

```
backend/
├── src/main/java/com/agriculture/
│   ├── controller/      # 接收 HTTP 请求，参数校验
│   ├── service/         # 业务逻辑
│   ├── mapper/          # 数据库操作（MyBatis-Plus）
│   ├── entity/          # 数据库表对应的实体类
│   ├── dto/             # 请求/响应数据传输对象
│   ├── config/          # Spring Security、CORS 等配置
│   └── common/          # 统一响应、异常处理、JWT 工具
├── src/main/resources/
│   ├── application.yml  # 数据库连接等配置
│   └── mapper/          # MyBatis XML（复杂 SQL）
└── pom.xml
```

### 开发顺序

1. 配通数据库连接 + 建表
2. 实现认证（JWT 登录注册）
3. 农场/地块 CRUD（最简单的增删改查）
4. 作物 CRUD
5. **病害诊断接口**（调用 C 的 AI 服务）
6. 农事任务 CRUD
7. 数据看板接口
8. 加 RBAC 权限控制

## 关键代码模式

### 1. application.yml 配置

```yaml
server:
  port: 8080

spring:
  datasource:
    url: jdbc:mysql://localhost:3306/agriculture?useUnicode=true&characterEncoding=utf-8&serverTimezone=Asia/Shanghai
    username: root
    password: 你的密码
    driver-class-name: com.mysql.cj.jdbc.Driver

mybatis-plus:
  configuration:
    map-underscore-to-camel-case: true  # 自动把数据库下划线转Java驼峰
  global-config:
    db-config:
      id-type: auto  # 主键自增

# JWT 密钥（自己随便写一串字符）
jwt:
  secret: agriculture-diagnosis-platform-2026-secret-key
  expiration: 86400000  # 24小时（毫秒）
```

### 2. 统一响应类

```java
// common/Result.java
@Data
public class Result<T> {
    private int code;
    private String message;
    private T data;

    public static <T> Result<T> ok(T data) {
        Result<T> r = new Result<>();
        r.code = 200;
        r.message = "success";
        r.data = data;
        return r;
    }

    public static <T> Result<T> error(int code, String message) {
        Result<T> r = new Result<>();
        r.code = code;
        r.message = message;
        return r;
    }
}
```

### 3. 实体类示例

```java
// entity/Field.java
@Data
@TableName("fields")
public class Field {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long farmId;
    private String name;
    private BigDecimal area;
    private String areaUnit;
    private String soilType;
    private String locationDesc;
    private String status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
```

### 4. Controller 示例

```java
// controller/FieldController.java
@RestController
@RequestMapping("/api/fields")
public class FieldController {

    @Autowired
    private FieldService fieldService;

    @GetMapping
    public Result<List<Field>> list(@RequestParam Long farmId) {
        return Result.ok(fieldService.listByFarm(farmId));
    }

    @PostMapping
    public Result<Field> create(@RequestBody @Valid FieldCreateDTO dto) {
        return Result.ok(fieldService.create(dto));
    }

    @GetMapping("/{id}")
    public Result<FieldDetailDTO> detail(@PathVariable Long id) {
        return Result.ok(fieldService.getDetail(id));
    }
}
```

### 5. 调用 C 的 AI 服务（核心）

```java
// service/DiagnosisService.java
@Service
public class DiagnosisService {

    @Autowired
    private RestTemplate restTemplate;

    public void callAiService(Long diagnosisId, MultipartFile image, 
                               String cropType, String growthStage, String location) {
        // 构建请求
        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        body.add("image", new ByteArrayResource(image.getBytes()) {
            @Override
            public String getFilename() { return image.getOriginalFilename(); }
        });
        body.add("crop_type", cropType);
        body.add("growth_stage", growthStage);
        body.add("field_location", location);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        // 调用 AI 服务
        String aiUrl = "http://localhost:8000/api/diagnose";
        ResponseEntity<AiDiagnosisResponse> response = restTemplate.postForEntity(
            aiUrl,
            new HttpEntity<>(body, headers),
            AiDiagnosisResponse.class
        );

        // 更新诊断记录
        updateDiagnosisRecord(diagnosisId, response.getBody());
    }
}
```

### 6. CORS 跨域配置（让前端能调）

```java
// config/CorsConfig.java
@Configuration
public class CorsConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
                .allowedOriginPatterns("*")
                .allowedMethods("*")
                .allowedHeaders("*")
                .allowCredentials(true);
    }
}
```

### 7. 诊断工单状态机

```
processing ──→ completed ──→ reviewed
                    │
                    └──→ rejected（需重新识别）
```

```java
public enum DiagnosisStatus {
    PROCESSING("processing"),
    COMPLETED("completed"),
    REVIEWED("reviewed"),
    REJECTED("rejected");
}
```

### 8. 图片上传处理

```java
@PostMapping("/diagnosis/upload")
public Result<DiagnosisUploadVO> upload(
        @RequestParam MultipartFile image,
        @RequestParam Long fieldId,
        @RequestParam Long cropId,
        @RequestParam(required = false) String description) {

    // 1. 校验文件
    if (image.isEmpty() || image.getSize() > 10 * 1024 * 1024) {
        return Result.error(400, "文件无效或超过10MB");
    }

    // 2. MinIO存图（先用本地替代）→ 实际用docker后用MinIO
    String imageUrl = saveImage(image);

    // 3. 创建观察记录
    Observation obs = observationService.create(fieldId, cropId, imageUrl, description);

    // 4. 创建诊断记录
    DiagnosisRecord record = diagnosisService.create(obs, imageUrl);

    // 5. 异步调用 AI 服务
    diagnosisService.callAiServiceAsync(record.getId(), image, ...);

    // 6. 立即返回
    DiagnosisUploadVO vo = new DiagnosisUploadVO();
    vo.setDiagnosisId(record.getId());
    vo.setStatus("processing");
    return Result.ok(vo);
}
```

## 数据库建表

把 `docs/schema.sql` 中的 SQL 拿到 MySQL 里执行：
```bash
mysql -u root -p
CREATE DATABASE agriculture CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE agriculture;
SOURCE C:/Users/你的用户名/Desktop/期末大作业/docs/schema.sql;
```

## MyBatis-Plus 三件套

对于每个表，你需要建三个文件：

1. **Entity**：对应数据库表
2. **Mapper**：继承 `BaseMapper<Entity>`，MyBatis-Plus 自动生成 CRUD
3. **Service**：业务逻辑 + `@Autowired Mapper`

MyBatis-Plus 内置方法（不用写 SQL）：
```java
fieldMapper.selectById(1L);           // 按ID查
fieldMapper.selectList(wrapper);      // 条件查询
fieldMapper.insert(entity);           // 插入
fieldMapper.updateById(entity);       // 按ID更新
fieldMapper.deleteById(1L);           // 按ID删除
```

## 调试技巧

1. **用 Postman 或 Apifox 测试接口**：先不写前端，直接发 HTTP 请求验证后端是否正常
2. **看控制台日志**：Spring Boot 日志会告诉你是哪里报错
3. **数据库可视化**：用 Navicat 或 DBeaver 连 MySQL 看数据

## 何时找李珈逾（AI 服务）

- AI 服务调不通（8000端口连不上）
- AI 返回的数据格式和文档不一致
- AI 服务报错
