package com.agriculture.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("fields")
public class Field {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long farmId;
    private String name;
    private java.math.BigDecimal area;
    private String areaUnit;
    private String soilType;
    private String locationDesc;
    private String status;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private LocalDateTime updatedAt;
}
