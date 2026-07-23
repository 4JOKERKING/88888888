package com.agriculture.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class TaskStatusRequest {
    @NotBlank(message = "状态不能为空")
    private String status;
}
