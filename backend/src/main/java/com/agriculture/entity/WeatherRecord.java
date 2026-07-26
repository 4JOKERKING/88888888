package com.agriculture.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@TableName("weather_records")
public class WeatherRecord {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String location;
    private LocalDate recordDate;
    private java.math.BigDecimal temperature;
    private java.math.BigDecimal humidity;
    private java.math.BigDecimal rainfall;
    private java.math.BigDecimal windSpeed;
    private String weatherDesc;
    private String dataSource;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
}
