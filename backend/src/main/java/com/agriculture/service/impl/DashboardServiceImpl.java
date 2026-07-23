package com.agriculture.service.impl;

import com.agriculture.service.DashboardService;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Service
@RequiredArgsConstructor
public class DashboardServiceImpl implements DashboardService {

    private final RestTemplate restTemplate;

    @Value("${ai.service.url}")
    private String aiServiceUrl;

    @Override
    public Map<String, Object> getWeather(String location, int days) {
        String url = aiServiceUrl + "/api/weather/" + location;
        return restTemplate.getForObject(url, Map.class);
    }

    @Override
    public Map<String, Object> getMarketPrices(String cropType, int days) {
        String url = aiServiceUrl + "/api/market-prices?crop_type=" + cropType + "&days=" + days;
        return restTemplate.getForObject(url, Map.class);
    }
}
