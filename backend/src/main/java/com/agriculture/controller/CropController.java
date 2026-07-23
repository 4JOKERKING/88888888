package com.agriculture.controller;

import com.agriculture.common.Result;
import com.agriculture.dto.CropRequest;
import com.agriculture.dto.CropUpdateRequest;
import com.agriculture.entity.Crop;
import com.agriculture.service.CropService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/crops")
@RequiredArgsConstructor
public class CropController {

    private final CropService cropService;

    @GetMapping
    public Result<List<Crop>> list(@RequestParam(required = false) Long fieldId) {
        if (fieldId == null) return Result.error(400, "fieldId 不能为空");
        return Result.ok(cropService.listByField(fieldId));
    }

    @PostMapping
    public Result<Crop> create(@Valid @RequestBody CropRequest request) {
        return Result.ok(cropService.create(request));
    }

    @PutMapping("/{id}")
    public Result<Crop> update(@PathVariable Long id, @Valid @RequestBody CropUpdateRequest request) {
        return Result.ok(cropService.update(id, request));
    }
}
