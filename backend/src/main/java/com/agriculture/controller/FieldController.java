package com.agriculture.controller;

import com.agriculture.common.Result;
import com.agriculture.dto.FieldRequest;
import com.agriculture.entity.Field;
import com.agriculture.service.FieldService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/fields")
@RequiredArgsConstructor
public class FieldController {

    private final FieldService fieldService;

    @GetMapping
    public Result<List<Field>> list(@RequestParam(required = false) Long farmId) {
        if (farmId == null) return Result.error(400, "farmId 不能为空");
        return Result.ok(fieldService.listByFarm(farmId));
    }

    @PostMapping
    public Result<Field> create(@Valid @RequestBody FieldRequest request) {
        return Result.ok(fieldService.create(request));
    }

    @GetMapping("/{id}")
    public Result<Field> getById(@PathVariable Long id) {
        return Result.ok(fieldService.getById(id));
    }
}
