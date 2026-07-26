package com.agriculture.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@TableName("farming_tasks")
public class FarmingTask {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long fieldId;
    private Long cropId;
    private String taskType;
    private String description;
    private LocalDate dueDate;
    private LocalDateTime completedAt;
    private String status;
    private String assignedTo;
    private Long sourceDiagnosisId;
    private String notes;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
}
