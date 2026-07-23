package com.agriculture.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;
import java.time.LocalDate;

@Data
public class TaskRequest {
    @NotNull(message = "地块不能为空")
    private Long fieldId;
    private Long cropId;
    @NotBlank(message = "任务类型不能为空")
    private String taskType;
    @NotBlank(message = "任务描述不能为空")
    private String description;
    private LocalDate dueDate;
    private String assignedTo;
}
