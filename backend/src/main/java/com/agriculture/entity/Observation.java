package com.agriculture.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("observations")
public class Observation {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long fieldId;
    private Long cropId;
    private Long userId;
    private String imageUrls;
    private String description;
    private String weatherCondition;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
}
