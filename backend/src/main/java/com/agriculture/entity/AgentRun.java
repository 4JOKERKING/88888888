package com.agriculture.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDateTime;

@Data
@TableName("agent_runs")
public class AgentRun {
    @TableId(type = IdType.AUTO)
    private Long id;
    private Long diagnosisId;
    private String agentType;
    private String inputSummary;
    private String outputSummary;
    private String citations;
    private Long durationMs;
    private String status;
    private String errorMessage;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
}
