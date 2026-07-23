package com.agriculture.controller;

import com.agriculture.common.Result;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class HealthController {

    @GetMapping("/api/health")
    public Result<Map<String, Object>> health() {
        return Result.ok(Map.of(
                "status", "ok",
                "service", "agriculture-backend",
                "version", "1.0.0"
        ));
    }
}
