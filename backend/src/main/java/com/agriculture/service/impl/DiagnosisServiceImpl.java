package com.agriculture.service.impl;

import com.agriculture.dto.ReviewRequest;
import com.agriculture.entity.*;
import com.agriculture.mapper.*;
import com.agriculture.service.AiDiagnosisClient;
import com.agriculture.service.DiagnosisService;
import com.agriculture.service.FileService;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

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
    private final AiDiagnosisClient aiDiagnosisClient;

    @Override
    public Map<String, Object> uploadImage(byte[] imageBytes, String filename, Long fieldId,
                                           Long cropId, String description, Long userId) {
        if (imageBytes.length > 10 * 1024 * 1024) {
            throw new RuntimeException("图片不能超过10MB");
        }

        String imageUrl = fileService.uploadBytes(imageBytes, filename);

        Observation observation = new Observation();
        observation.setFieldId(fieldId);
        observation.setCropId(cropId);
        observation.setUserId(userId);
        observation.setImageUrls("["" + imageUrl + ""]");
        observation.setDescription(description);
        observationMapper.insert(observation);

        Crop crop = cropMapper.selectById(cropId);

        DiagnosisRecord record = new DiagnosisRecord();
        record.setObservationId(observation.getId());
        record.setFieldId(fieldId);
        record.setCropId(cropId);
        record.setImageUrl(imageUrl);
        record.setStatus("processing");
        diagnosisMapper.insert(record);

        // 通过独立 Bean 调用，@Async 真正生效
        aiDiagnosisClient.diagnose(record.getId(), imageBytes, filename,
                crop != null ? crop.getCropType() : "未知",
                crop != null ? crop.getGrowthStage() : "未知",
                getFieldLocation(fieldId));

        Map<String, Object> data = new HashMap<>();
        data.put("diagnosisId", record.getId());
        data.put("status", "processing");
        return data;
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
