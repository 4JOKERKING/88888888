package com.agriculture.service.impl;

import com.agriculture.dto.ReviewRequest;
import com.agriculture.entity.*;
import com.agriculture.mapper.*;
import com.agriculture.service.DiagnosisService;
import com.agriculture.service.FileService;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.*;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
public class DiagnosisServiceImpl implements DiagnosisService {

    private final DiagnosisRecordMapper diagnosisMapper;
    private final CropMapper cropMapper;
    private final FieldMapper fieldMapper;
    private final ObservationMapper observationMapper;
    private final FileService fileService;
    private final RestTemplate restTemplate;

    @Value("${ai.service.url}")
    private String aiServiceUrl;

    @Override
    public Map<String, Object> uploadImage(byte[] imageBytes, String filename, Long fieldId,
                                           Long cropId, String description, Long userId) {
        // 1. 校验图片格式和大小
        if (imageBytes.length > 10 * 1024 * 1024) {
            throw new RuntimeException("图片不能超过10MB");
        }

        // 2. 存图片到本地
        String imageUrl = fileService.uploadBytes(imageBytes, filename);

        // 3. 创建观察记录
        Observation observation = new Observation();
        observation.setFieldId(fieldId);
        observation.setCropId(cropId);
        observation.setUserId(userId);
        observation.setImageUrls("["" + imageUrl + ""]");
        observation.setDescription(description);
        observationMapper.insert(observation);

        // 4. 查询作物信息
        Crop crop = cropMapper.selectById(cropId);

        // 5. 创建诊断记录
        DiagnosisRecord record = new DiagnosisRecord();
        record.setObservationId(observation.getId());
        record.setFieldId(fieldId);
        record.setCropId(cropId);
        record.setImageUrl(imageUrl);
        record.setStatus("processing");
        diagnosisMapper.insert(record);

        // 6. 异步调用AI服务
        callAiService(record.getId(), imageBytes, filename,
                crop != null ? crop.getCropType() : "未知",
                crop != null ? crop.getGrowthStage() : "未知",
                getFieldLocation(fieldId));

        // 7. 返回诊断ID
        Map<String, Object> data = new HashMap<>();
        data.put("diagnosisId", record.getId());
        data.put("status", "processing");
        return data;
    }

    @Async
    public void callAiService(Long diagnosisId, byte[] imageBytes, String filename,
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
        record.setRecognitionResult(com.alibaba.fastjson.JSON.toJSONString(aiResult));
        record.setRagSuggestion(com.alibaba.fastjson.JSON.toJSONString(aiResult.get("rag_result")));
        record.setAgentOpinion(com.alibaba.fastjson.JSON.toJSONString(aiResult.get("agent_opinion")));

        Object agentOpinion = aiResult.get("agent_opinion");
        if (agentOpinion instanceof Map) {
            record.setRiskLevel((String) ((Map<?, ?>) agentOpinion).get("risk_level"));
        }
        record.setStatus("completed");
        diagnosisMapper.updateById(record);
    }

    private String getFieldLocation(Long fieldId) {
        Field field = fieldMapper.selectById(fieldId);
        return field != null ? field.getLocationDesc() : "未知";
    }

    @Override
    public DiagnosisRecord getById(Long id) {
        return diagnosisMapper.selectById(id);
    }

    @Override
    public IPage<DiagnosisRecord> listByPage(Long fieldId, String status, int page, int size) {
        Page<DiagnosisRecord> pageObj = new Page<>(page, size);
        LambdaQueryWrapper<DiagnosisRecord> wrapper = new LambdaQueryWrapper<DiagnosisRecord>()
                .orderByDesc(DiagnosisRecord::getCreatedAt);
        if (fieldId != null) wrapper.eq(DiagnosisRecord::getFieldId, fieldId);
        if (status != null && !status.isEmpty()) wrapper.eq(DiagnosisRecord::getStatus, status);
        return diagnosisMapper.selectPage(pageObj, wrapper);
    }

    @Override
    public void review(Long id, ReviewRequest request, Long reviewerId) {
        DiagnosisRecord record = diagnosisMapper.selectById(id);
        if (record == null) throw new RuntimeException("诊断记录不存在");

        if ("approve".equals(request.getAction())) {
            record.setStatus("reviewed");
        } else if ("reject".equals(request.getAction())) {
            record.setStatus("rejected");
        } else {
            throw new RuntimeException("无效的审核操作");
        }
        record.setReviewComment(request.getComment());
        record.setReviewedBy(reviewerId);
        record.setReviewedAt(LocalDateTime.now());
        diagnosisMapper.updateById(record);
    }
}
