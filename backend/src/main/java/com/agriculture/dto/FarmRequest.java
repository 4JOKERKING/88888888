package com.agriculture.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class FarmRequest {
    @NotBlank(message = "农场名称不能为空")
    private String name;
    private String address;
    private String description;
}
