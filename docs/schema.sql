-- =============================================
-- 农业智能诊断平台 数据库建表脚本
-- MySQL 8.0+
-- 使用方法：mysql -u root -p < schema.sql
-- =============================================

CREATE DATABASE IF NOT EXISTS agriculture
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE agriculture;

-- =============================================
-- 1. 用户表
-- =============================================
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    password_hash VARCHAR(255) NOT NULL COMMENT 'BCrypt加密密码',
    real_name VARCHAR(50) NOT NULL COMMENT '真实姓名',
    phone VARCHAR(20) COMMENT '手机号',
    role ENUM('farmer','technician','manager','admin') NOT NULL DEFAULT 'farmer' COMMENT '角色',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '1=正常 0=禁用',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_role (role),
    INDEX idx_users_status (status)
) ENGINE=InnoDB COMMENT='用户表';

-- =============================================
-- 2. 农场表
-- =============================================
CREATE TABLE farms (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '农场名称',
    address VARCHAR(255) COMMENT '地址',
    description TEXT COMMENT '描述',
    owner_id BIGINT COMMENT '农场主',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='农场表';

-- =============================================
-- 3. 地块表
-- =============================================
CREATE TABLE fields (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    farm_id BIGINT NOT NULL COMMENT '所属农场',
    name VARCHAR(100) NOT NULL COMMENT '地块名称',
    area DECIMAL(10,2) COMMENT '面积（亩）',
    area_unit VARCHAR(10) DEFAULT '亩' COMMENT '面积单位',
    soil_type VARCHAR(50) COMMENT '土壤类型',
    location_desc VARCHAR(255) COMMENT '位置描述',
    status ENUM('active','fallow','abandoned') NOT NULL DEFAULT 'active' COMMENT '地块状态',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
    INDEX idx_fields_farm (farm_id),
    INDEX idx_fields_status (status)
) ENGINE=InnoDB COMMENT='地块表';

-- =============================================
-- 4. 作物表
-- =============================================
CREATE TABLE crops (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    field_id BIGINT NOT NULL COMMENT '所在地块',
    crop_type VARCHAR(50) NOT NULL COMMENT '作物类型',
    variety VARCHAR(100) COMMENT '品种',
    plant_date DATE COMMENT '种植日期',
    plant_area DECIMAL(10,2) COMMENT '种植面积',
    area_unit VARCHAR(10) DEFAULT '亩',
    growth_stage VARCHAR(50) COMMENT '生育期',
    status ENUM('growing','harvested','diseased','dead') NOT NULL DEFAULT 'growing' COMMENT '生长状态',
    notes TEXT COMMENT '备注',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE,
    INDEX idx_crops_field (field_id),
    INDEX idx_crops_type (crop_type),
    INDEX idx_crops_status (status)
) ENGINE=InnoDB COMMENT='作物表';

-- =============================================
-- 5. 种植周期表
-- =============================================
CREATE TABLE planting_cycles (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    field_id BIGINT NOT NULL,
    crop_id BIGINT NOT NULL,
    start_date DATE NOT NULL COMMENT '开始日期',
    end_date DATE COMMENT '预计结束日期',
    actual_end_date DATE COMMENT '实际结束日期',
    status ENUM('active','completed','failed') NOT NULL DEFAULT 'active',
    yield_amount DECIMAL(10,2) COMMENT '产量',
    yield_unit VARCHAR(10) DEFAULT '公斤' COMMENT '产量单位',
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE,
    FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE CASCADE,
    INDEX idx_cycles_field (field_id),
    INDEX idx_cycles_crop (crop_id)
) ENGINE=InnoDB COMMENT='种植周期表';

-- =============================================
-- 6. 观察记录表
-- =============================================
CREATE TABLE observations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    field_id BIGINT NOT NULL,
    crop_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL COMMENT '上报人',
    image_urls TEXT COMMENT '图片URL列表（JSON数组）',
    description TEXT COMMENT '文字描述',
    weather_condition VARCHAR(100) COMMENT '观察时天气',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE,
    FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_observations_field (field_id),
    INDEX idx_observations_user (user_id),
    INDEX idx_observations_created (created_at)
) ENGINE=InnoDB COMMENT='观察记录表';

-- =============================================
-- 7. 诊断记录表 ⭐核心
-- =============================================
CREATE TABLE diagnosis_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    observation_id BIGINT COMMENT '关联观察记录',
    field_id BIGINT NOT NULL,
    crop_id BIGINT NOT NULL,
    image_url VARCHAR(500) COMMENT 'MinIO图片地址',
    model_version VARCHAR(50) COMMENT '模型版本',
    recognition_result JSON COMMENT '图像识别原始结果',
    rag_suggestion JSON COMMENT 'RAG检索的防治建议',
    agent_opinion JSON COMMENT 'Agent综合研判结果',
    risk_level ENUM('low','medium','high','critical') COMMENT '风险等级',
    confidence DECIMAL(5,4) COMMENT '置信度',
    status ENUM('processing','completed','reviewed','rejected') NOT NULL DEFAULT 'processing' COMMENT '诊断状态',
    reviewed_by BIGINT COMMENT '审核人（农技人员）',
    review_comment TEXT COMMENT '审核意见',
    reviewed_at DATETIME COMMENT '审核时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (observation_id) REFERENCES observations(id) ON DELETE SET NULL,
    FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE,
    FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_diagnosis_field (field_id),
    INDEX idx_diagnosis_crop (crop_id),
    INDEX idx_diagnosis_status (status),
    INDEX idx_diagnosis_risk (risk_level),
    INDEX idx_diagnosis_created (created_at)
) ENGINE=InnoDB COMMENT='诊断记录表（核心）';

-- =============================================
-- 8. 农事任务表
-- =============================================
CREATE TABLE farming_tasks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    field_id BIGINT NOT NULL,
    crop_id BIGINT COMMENT '关联作物',
    task_type ENUM('spray','fertilize','irrigate','prune','harvest','other') NOT NULL COMMENT '任务类型',
    description TEXT NOT NULL COMMENT '任务描述',
    due_date DATE COMMENT '截止日期',
    completed_at DATETIME COMMENT '完成时间',
    status ENUM('pending','in_progress','completed','cancelled') NOT NULL DEFAULT 'pending' COMMENT '任务状态',
    assigned_to VARCHAR(50) COMMENT '负责人',
    source_diagnosis_id BIGINT COMMENT '来源诊断ID',
    notes TEXT COMMENT '备注',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE,
    FOREIGN KEY (crop_id) REFERENCES crops(id) ON DELETE SET NULL,
    FOREIGN KEY (source_diagnosis_id) REFERENCES diagnosis_records(id) ON DELETE SET NULL,
    INDEX idx_tasks_field (field_id),
    INDEX idx_tasks_status (status),
    INDEX idx_tasks_due (due_date),
    INDEX idx_tasks_type (task_type)
) ENGINE=InnoDB COMMENT='农事任务表';

-- =============================================
-- 9. 天气记录表
-- =============================================
CREATE TABLE weather_records (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    location VARCHAR(100) NOT NULL COMMENT '地点',
    record_date DATE NOT NULL COMMENT '日期',
    temperature DECIMAL(5,1) COMMENT '温度（℃）',
    humidity DECIMAL(5,1) COMMENT '湿度（%）',
    rainfall DECIMAL(8,2) COMMENT '降雨量（mm）',
    wind_speed DECIMAL(5,1) COMMENT '风速（m/s）',
    weather_desc VARCHAR(50) COMMENT '天气描述',
    data_source VARCHAR(100) COMMENT '数据来源',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_location_date (location, record_date),
    INDEX idx_weather_date (record_date)
) ENGINE=InnoDB COMMENT='天气记录表';

-- =============================================
-- 10. 市场价格表
-- =============================================
CREATE TABLE market_prices (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    crop_type VARCHAR(50) NOT NULL COMMENT '作物类型',
    variety VARCHAR(100) COMMENT '品种',
    price DECIMAL(10,2) NOT NULL COMMENT '价格',
    unit VARCHAR(20) DEFAULT '元/公斤' COMMENT '单位',
    market VARCHAR(100) COMMENT '市场名称',
    record_date DATE NOT NULL COMMENT '日期',
    data_source VARCHAR(100) COMMENT '数据来源',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_market_crop_date (crop_type, record_date),
    INDEX idx_market_date (record_date)
) ENGINE=InnoDB COMMENT='市场价格表';

-- =============================================
-- 11. 知识文档表（RAG知识库）
-- =============================================
CREATE TABLE knowledge_documents (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL COMMENT '文档标题',
    content LONGTEXT COMMENT '文档内容',
    category VARCHAR(50) COMMENT '分类',
    crop_type VARCHAR(50) COMMENT '适用作物',
    source VARCHAR(200) COMMENT '来源',
    version VARCHAR(20) DEFAULT '1.0' COMMENT '版本号',
    vector_id VARCHAR(100) COMMENT '向量库ID',
    status TINYINT NOT NULL DEFAULT 1 COMMENT '1=启用 0=停用',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_knowledge_category (category),
    INDEX idx_knowledge_crop (crop_type),
    INDEX idx_knowledge_status (status)
) ENGINE=InnoDB COMMENT='知识文档表';

-- =============================================
-- 12. 模型版本表
-- =============================================
CREATE TABLE model_versions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL COMMENT '模型名称',
    model_type VARCHAR(50) COMMENT '类型',
    version VARCHAR(20) NOT NULL COMMENT '版本号',
    file_path VARCHAR(500) COMMENT '模型文件路径',
    accuracy DECIMAL(5,4) COMMENT '准确率',
    parameters JSON COMMENT '超参数',
    status ENUM('active','archived','failed') NOT NULL DEFAULT 'active',
    deployed_at DATETIME COMMENT '部署时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_model_status (status)
) ENGINE=InnoDB COMMENT='模型版本表';

-- =============================================
-- 13. Agent执行记录表
-- =============================================
CREATE TABLE agent_runs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    diagnosis_id BIGINT COMMENT '关联诊断',
    agent_type VARCHAR(50) COMMENT 'Agent类型',
    input_summary TEXT COMMENT '输入摘要',
    output_summary TEXT COMMENT '输出摘要',
    citations JSON COMMENT '引用知识文档ID列表',
    duration_ms BIGINT COMMENT '执行耗时（毫秒）',
    status ENUM('success','failed','timeout') COMMENT '执行状态',
    error_message TEXT COMMENT '错误信息',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (diagnosis_id) REFERENCES diagnosis_records(id) ON DELETE SET NULL,
    INDEX idx_agent_diagnosis (diagnosis_id),
    INDEX idx_agent_status (status)
) ENGINE=InnoDB COMMENT='Agent执行记录表';

-- =============================================
-- 14. 审计日志表
-- =============================================
CREATE TABLE audit_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT COMMENT '操作人',
    action VARCHAR(50) NOT NULL COMMENT '操作类型',
    target_type VARCHAR(50) COMMENT '操作对象类型',
    target_id BIGINT COMMENT '操作对象ID',
    detail JSON COMMENT '操作详情',
    ip_address VARCHAR(50) COMMENT 'IP地址',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_audit_user (user_id),
    INDEX idx_audit_action (action),
    INDEX idx_audit_created (created_at)
) ENGINE=InnoDB COMMENT='审计日志表';

-- =============================================
-- 种子数据
-- =============================================

-- 测试用户（密码都是 123456，BCrypt加密）
INSERT INTO users (username, password_hash, real_name, phone, role) VALUES
('admin', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5Eh', '管理员张', '13800000001', 'admin'),
('farmer1', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5Eh', '农户李', '13800000002', 'farmer'),
('tech1', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5Eh', '农技员王', '13800000003', 'technician'),
('manager1', '$2a$10$N.zmdr9k7uOCQb376NoUnuTJ8iAt6Z5EHsM8lE9lBOsl7iAt6Z5Eh', '社长赵', '13800000004', 'manager');

-- 示例农场
INSERT INTO farms (id, name, address, description, owner_id) VALUES
(1, '阳光农场', '云南省昆明市呈贡区七甸街道', '以蔬菜和花卉种植为主的家庭农场', 2);

-- 示例地块
INSERT INTO fields (id, farm_id, name, area, soil_type, location_desc, status) VALUES
(1, 1, 'A区-蔬菜地1号', 2.5, '红壤', '农场东侧，靠近灌溉渠', 'active'),
(2, 1, 'A区-蔬菜地2号', 1.8, '红壤', '农场东侧，大棚区', 'active'),
(3, 1, 'B区-花卉大棚', 3.0, '水稻土', '农场西侧，温室大棚', 'active');

-- 示例作物
INSERT INTO crops (id, field_id, crop_type, variety, plant_date, plant_area, growth_stage, status) VALUES
(1, 1, '番茄', '粉果1号', '2026-03-15', 2.0, '开花坐果期', 'growing'),
(2, 2, '辣椒', '线椒3号', '2026-04-01', 1.8, '结果期', 'growing'),
(3, 3, '花卉', '切花玫瑰', '2026-02-20', 3.0, '采收期', 'growing');

-- 种植周期
INSERT INTO planting_cycles (field_id, crop_id, start_date, end_date, status) VALUES
(1, 1, '2026-03-15', '2026-07-30', 'active'),
(2, 2, '2026-04-01', '2026-08-15', 'active'),
(3, 3, '2026-02-20', '2026-06-30', 'active');

-- 示例农技知识文档
INSERT INTO knowledge_documents (title, content, category, crop_type, source) VALUES
('番茄晚疫病防治技术', '晚疫病是番茄主要真菌病害之一。发病条件：气温18-22℃，相对湿度85%以上。症状：叶片出现水渍状暗绿色斑点，湿度大时叶背出现白色霉层。防治方法：1. 选用抗病品种 2. 合理密植，加强通风 3. 发病初期喷洒霜脲·锰锌可湿性粉剂500倍液 4. 每7天喷洒一次，连续2-3次 5. 及时清除病叶病果', '病害防治', '番茄', '《云南省番茄主要病虫害防治技术规范》2024版'),
('番茄早疫病防治技术', '早疫病又称轮纹病，主要危害叶片和茎秆。症状：叶片出现圆形或近圆形褐色病斑，有明显同心轮纹。防治方法：1. 轮作倒茬，避免连作 2. 发病初期用代森锰锌可湿性粉剂500倍液喷雾 3. 加强肥水管理，增施磷钾肥', '病害防治', '番茄', '《云南省番茄主要病虫害防治技术规范》2024版'),
('辣椒炭疽病防治技术', '炭疽病主要危害辣椒果实。症状：果实表面出现圆形凹陷黑褐色病斑，有同心轮纹。防治方法：1. 选用抗病品种 2. 合理密植 3. 发病初期喷洒咪鲜胺1500倍液 4. 及时摘除病果', '病害防治', '辣椒', '《云南省辣椒病虫害绿色防控技术手册》'),
('花卉白粉病防治技术', '白粉病是花卉常见病害。症状：叶片和嫩茎表面覆盖白色粉状物，严重时叶片卷曲。防治方法：1. 加强通风透光 2. 合理施肥，避免偏施氮肥 3. 发病初期喷洒三唑酮可湿性粉剂1000倍液 4. 清除病残体', '病害防治', '花卉', '《云南花卉常见病害防治手册》');

-- 模型版本记录
INSERT INTO model_versions (model_name, model_type, version, accuracy, status, deployed_at) VALUES
('plant-disease-resnet50', 'image_classification', '2.1.0', 0.9100, 'active', NOW()),
('agriculture-rag', 'rag', '1.0.0', NULL, 'active', NOW());
