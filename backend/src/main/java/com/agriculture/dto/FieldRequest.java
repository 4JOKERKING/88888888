package com.agriculture.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;
import java.math.BigDecimal;

@Data
public class FieldRequest {
    @NotNull(message = "所属农场不能为空")
    private Long farmId;
    @NotBlank(message = "地块名称不能为空")
    private String name;
    private BigDecimal area;
    private String areaUnit;
    private String soilType;
    private String locationDesc;
}
