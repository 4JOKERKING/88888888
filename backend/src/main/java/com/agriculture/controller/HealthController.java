package com.agriculture.controller;

import com.agriculture.common.Result;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.sql.DataSource;
import java.sql.Connection;
import java.util.HashMap;
import java.util.Map;

@RestController
public class HealthController {

    private final DataSource dataSource;

    public HealthController(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @GetMapping("/api/health")
    public Result<Map<String, Object>> health() {
        Map<String, Object> info = new HashMap<>();
        info.put("status", "ok");
        info.put("service", "agriculture-backend");
        info.put("version", "1.0.0");

        // 检查数据库连接
        try (Connection conn = dataSource.getConnection()) {
            info.put("database", conn.isValid(3) ? "connected" : "disconnected");
        } catch (Exception e) {
            info.put("database", "disconnected");
            info.put("dbError", e.getMessage());
        }

        return Result.ok(info);
    }
}
