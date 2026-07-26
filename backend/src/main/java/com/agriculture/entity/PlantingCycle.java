package com.agriculture.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@TableName("planting_cycles")
public class PlantingCycle {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long fieldId;
    private Long cropId;
    private LocalDate startDate;
    private LocalDate endDate;
    private LocalDate actualEndDate;
    private String status;
    private java.math.BigDecimal yieldAmount;
    private String yieldUnit;
    private String notes;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
}
