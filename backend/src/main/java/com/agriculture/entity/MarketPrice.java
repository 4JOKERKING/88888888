package com.agriculture.entity;

import com.baomidou.mybatisplus.annotation.*;
import lombok.Data;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Data
@TableName("market_prices")
public class MarketPrice {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String cropType;
    private String variety;
    private java.math.BigDecimal price;
    private String unit;
    private String market;
    private LocalDate recordDate;
    private String dataSource;
    @TableField(fill = FieldFill.INSERT)
    private LocalDateTime createdAt;
}
