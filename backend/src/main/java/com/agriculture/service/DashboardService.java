package com.agriculture.service;

import java.util.Map;

public interface DashboardService {
    Map<String, Object> getWeather(String location, int days);
    Map<String, Object> getMarketPrices(String cropType, int days);
}
