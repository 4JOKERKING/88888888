package com.agriculture.service.impl;

import com.agriculture.service.DashboardService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class DashboardServiceImpl implements DashboardService {

    private final RestTemplate restTemplate;

    @Value("${ai.service.url}")
    private String aiServiceUrl;

    @Override
    public Map<String, Object> getWeather(String location, int days) {
        String url = aiServiceUrl + "/api/weather/" + location;
        try {
            return restTemplate.getForObject(url, Map.class);
        } catch (RestClientException e) {
            log.warn("天气服务不可用 location={}", location, e);
            return Map.of("location", location, "error", "天气数据暂不可用，请稍后重试");
        }
    }

    @Override
    public Map<String, Object> getMarketPrices(String cropType, int days) {
        String url = aiServiceUrl + "/api/market-prices?crop_type=" + cropType + "&days=" + days;
        try {
            return restTemplate.getForObject(url, Map.class);
        } catch (RestClientException e) {
            log.warn("市场价格服务不可用 cropType={}", cropType, e);
            return Map.of("cropType", cropType, "error", "市场价格数据暂不可用，请稍后重试");
        }
    }
}
