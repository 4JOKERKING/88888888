package com.agriculture.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("model_versions")
public class ModelVersion {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String modelName;
    private String modelType;
    private String version;
    private String filePath;
    private java.math.BigDecimal accuracy;
    private String parameters;
    private String status;
    private LocalDateTime deployedAt;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
}
