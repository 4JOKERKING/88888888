package com.agriculture.controller;

import com.agriculture.common.Result;
import com.agriculture.service.DashboardService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class DashboardController {

    private final DashboardService dashboardService;

    @GetMapping("/weather")
    public Result<Map<String, Object>> getWeather(
            @RequestParam String location,
            @RequestParam(defaultValue = "7") int days) {
        return Result.ok(dashboardService.getWeather(location, days));
    }

    @GetMapping("/market-prices")
    public Result<Map<String, Object>> getMarketPrices(
            @RequestParam String cropType,
            @RequestParam(defaultValue = "30") int days) {
        return Result.ok(dashboardService.getMarketPrices(cropType, days));
    }
}
