package com.agriculture.service;

import com.agriculture.dto.ReviewRequest;
import com.agriculture.entity.DiagnosisRecord;
import com.baomidou.mybatisplus.core.metadata.IPage;

import java.util.Map;

public interface DiagnosisService {
    Map<String, Object> uploadImage(byte[] imageBytes, String filename, Long fieldId,
                                     Long cropId, String description, Long userId);
    DiagnosisRecord getById(Long id);
    IPage<DiagnosisRecord> listByPage(Long fieldId, String status, int page, int size);
    void review(Long id, ReviewRequest request, Long reviewerId);
}
