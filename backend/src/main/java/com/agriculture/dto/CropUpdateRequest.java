package com.agriculture.dto;

import lombok.Data;

@Data
public class CropUpdateRequest {
    private String growthStage;
    private String status;
}
