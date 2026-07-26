package com.agriculture.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;

@Data
public class CropRequest {
    @NotNull(message = "所在地块不能为空")
    private Long fieldId;
    @NotBlank(message = "作物类型不能为空")
    private String cropType;
    private String variety;
    private LocalDate plantDate;
    private BigDecimal plantArea;
    private String areaUnit;
    private String growthStage;
    private String notes;
}
