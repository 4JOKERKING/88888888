package com.agriculture.service;

import com.agriculture.entity.DiagnosisRecord;
import com.agriculture.entity.Field;
import com.agriculture.mapper.DiagnosisRecordMapper;
import com.agriculture.mapper.FieldMapper;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.*;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;

import java.math.BigDecimal;
import java.util.Map;

/**
 * AI 诊断服务客户端 — 独立 Bean 确保 @Async 通过代理生效
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AiDiagnosisClient {

    private final DiagnosisRecordMapper diagnosisMapper;
    private final FieldMapper fieldMapper;
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    @Value("${ai.service.url}")
    private String aiServiceUrl;

    @Async
    public void diagnose(Long diagnosisId, byte[] imageBytes, String filename,
                         String cropType, String growthStage, String location) {
        try {
            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("image", new ByteArrayResource(imageBytes) {
                @Override
                public String getFilename() { return filename; }
            });
            body.add("crop_type", cropType);
            body.add("growth_stage", growthStage);
            body.add("field_location", location);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);

            String aiUrl = aiServiceUrl + "/api/diagnose";
            ResponseEntity<Map> response = restTemplate.postForEntity(
                    aiUrl, new HttpEntity<>(body, headers), Map.class);

            Map<String, Object> result = response.getBody();
            if (result != null) {
                updateDiagnosisRecord(diagnosisId, result);
            }
        } catch (Exception e) {
            log.error("AI诊断失败 diagnosisId={}", diagnosisId, e);
            DiagnosisRecord record = diagnosisMapper.selectById(diagnosisId);
            if (record != null) {
                record.setStatus("failed");
                diagnosisMapper.updateById(record);
            }
        }
    }

    private void updateDiagnosisRecord(Long id, Map<String, Object> aiResult) {
        DiagnosisRecord record = diagnosisMapper.selectById(id);
        if (record == null) return;

        record.setDisease((String) aiResult.get("disease"));
        Object confidence = aiResult.get("confidence");
        if (confidence instanceof Number) {
            record.setConfidence(BigDecimal.valueOf(((Number) confidence).doubleValue()));
        }
        record.setSeverity((String) aiResult.get("severity"));

        // 用 Jackson 序列化（替换 fastjson），前端直接拿到对象
        try {
            record.setRecognitionResult(objectMapper.writeValueAsString(aiResult));

            Object ragResult = aiResult.get("rag_result");
            if (ragResult != null) {
                record.setRagSuggestion(objectMapper.writeValueAsString(ragResult));
            }

            Object agentOpinion = aiResult.get("agent_opinion");
            if (agentOpinion != null) {
                record.setAgentOpinion(objectMapper.writeValueAsString(agentOpinion));
                if (agentOpinion instanceof Map) {
                    record.setRiskLevel((String) ((Map<?, ?>) agentOpinion).get("risk_level"));
                }
            }
        } catch (Exception e) {
            log.error("序列化诊断结果失败 diagnosisId={}", id, e);
        }

        record.setStatus("completed");
        diagnosisMapper.updateById(record);
    }
}
