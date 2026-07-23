package com.agriculture.controller;

import com.agriculture.common.PageResult;
import com.agriculture.common.Result;
import com.agriculture.common.UserContext;
import com.agriculture.dto.ReviewRequest;
import com.agriculture.entity.DiagnosisRecord;
import com.agriculture.service.DiagnosisService;
import com.baomidou.mybatisplus.core.metadata.IPage;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.Map;

@RestController
@RequestMapping("/api/diagnosis")
@RequiredArgsConstructor
public class DiagnosisController {

    private final DiagnosisService diagnosisService;

    @PostMapping("/upload")
    public Result<Map<String, Object>> upload(
            @RequestParam MultipartFile image,
            @RequestParam Long fieldId,
            @RequestParam Long cropId,
            @RequestParam(required = false) String description) {

        String filename = image.getOriginalFilename();
        if (filename != null && !filename.toLowerCase().matches(".*\\.(jpg|jpeg|png)$")) {
            return Result.error(400, "仅支持 JPG/PNG 格式图片");
        }
        try {
            byte[] bytes = image.getBytes();
            Long userId = UserContext.getUserId();
            return Result.ok(diagnosisService.uploadImage(bytes,
                    image.getOriginalFilename(), fieldId, cropId, description, userId));
        } catch (Exception e) {
            return Result.error(500, "上传失败: " + e.getMessage());
        }
    }

    @GetMapping("/{id}")
    public Result<DiagnosisRecord> getResult(@PathVariable Long id) {
        return Result.ok(diagnosisService.getById(id));
    }

    @GetMapping("/list")
    public Result<PageResult<DiagnosisRecord>> list(
            @RequestParam(required = false) Long fieldId,
            @RequestParam(required = false) String status,
            @RequestParam(defaultValue = "1") int page,
            @RequestParam(defaultValue = "20") int size) {
        IPage<DiagnosisRecord> result = diagnosisService.listByPage(fieldId, status, page, size);
        return Result.ok(new PageResult<>(
                result.getRecords(), result.getTotal(), (int) result.getCurrent(), (int) result.getSize()));
    }

    @PutMapping("/{id}/review")
    public Result<String> review(@PathVariable Long id, @Valid @RequestBody ReviewRequest request) {
        String role = UserContext.getRole();
        if (!"technician".equals(role) && !"manager".equals(role) && !"admin".equals(role)) {
            return Result.forbidden("仅农技人员和管理员可审核诊断结果");
        }
        Long reviewerId = UserContext.getUserId();
        diagnosisService.review(id, request, reviewerId);
        return Result.ok("审核完成");
    }
}
