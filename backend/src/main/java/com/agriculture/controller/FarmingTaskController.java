package com.agriculture.controller;

import com.agriculture.common.Result;
import com.agriculture.dto.TaskRequest;
import com.agriculture.dto.TaskStatusRequest;
import com.agriculture.entity.FarmingTask;
import com.agriculture.service.FarmingTaskService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/tasks")
@RequiredArgsConstructor
public class FarmingTaskController {

    private final FarmingTaskService taskService;

    @GetMapping
    public Result<List<FarmingTask>> list(
            @RequestParam(required = false) Long fieldId,
            @RequestParam(required = false) String status) {
        return Result.ok(taskService.listByField(fieldId, status));
    }

    @PostMapping
    public Result<FarmingTask> create(@Valid @RequestBody TaskRequest request) {
        return Result.ok(taskService.create(request));
    }

    @PutMapping("/{id}/status")
    public Result<FarmingTask> updateStatus(@PathVariable Long id,
                                             @Valid @RequestBody TaskStatusRequest request) {
        return Result.ok(taskService.updateStatus(id, request));
    }
}
