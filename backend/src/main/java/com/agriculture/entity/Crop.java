package com.agriculture.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@TableName("crops")
public class Crop {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long fieldId;
    private String cropType;
    private String variety;
    private LocalDate plantDate;
    private java.math.BigDecimal plantArea;
    private String areaUnit;
    private String growthStage;
    private String status;
    private String notes;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;
}
