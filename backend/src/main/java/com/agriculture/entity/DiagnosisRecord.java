package com.agriculture.entity;

import com.baomidou.mybatisplus.annotation.*;
import com.fasterxml.jackson.annotation.JsonRawValue;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@TableName("diagnosis_records")
public class DiagnosisRecord {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long observationId;
    private Long fieldId;
    private Long cropId;
    private String imageUrl;
    private String disease;
    private BigDecimal confidence;
    private String severity;
    private String modelVersion;
    @JsonRawValue
    private String recognitionResult;
    @JsonRawValue
    private String ragSuggestion;
    @JsonRawValue
    private String agentOpinion;
    private String riskLevel;
    private String status;
    private Long reviewedBy;
    private String reviewComment;
    private LocalDateTime reviewedAt;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
}
