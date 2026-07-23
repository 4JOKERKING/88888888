package com.agriculture.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class ReviewRequest {
    @NotBlank(message = "操作不能为空")
    private String action;
    private String comment;
}
