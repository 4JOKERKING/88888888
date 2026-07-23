package com.agriculture.controller;

import com.agriculture.common.Result;
import com.agriculture.common.UserContext;
import com.agriculture.dto.FarmRequest;
import com.agriculture.entity.Farm;
import com.agriculture.service.FarmService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/farms")
@RequiredArgsConstructor
public class FarmController {

    private final FarmService farmService;

    @GetMapping
    public Result<List<Farm>> list() {
        Long userId = UserContext.getUserId();
        return Result.ok(farmService.listByUser(userId));
    }

    @PostMapping
    public Result<Farm> create(@Valid @RequestBody FarmRequest request) {
        Long userId = UserContext.getUserId();
        return Result.ok(farmService.create(request, userId));
    }
}
