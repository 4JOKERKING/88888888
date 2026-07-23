package com.agriculture.service.impl;

import com.agriculture.dto.FieldRequest;
import com.agriculture.entity.Crop;
import com.agriculture.entity.Field;
import com.agriculture.mapper.CropMapper;
import com.agriculture.mapper.FieldMapper;
import com.agriculture.service.FieldService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class FieldServiceImpl implements FieldService {

    private final FieldMapper fieldMapper;
    private final CropMapper cropMapper;

    @Override
    public List<Field> listByFarm(Long farmId) {
        return fieldMapper.selectList(
                new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<Field>()
                        .eq(Field::getFarmId, farmId));
    }

    @Override
    public Field create(FieldRequest request) {
        Field field = new Field();
        field.setFarmId(request.getFarmId());
        field.setName(request.getName());
        field.setArea(request.getArea());
        field.setAreaUnit(request.getAreaUnit());
        field.setSoilType(request.getSoilType());
        field.setLocationDesc(request.getLocationDesc());
        field.setStatus("active");
        fieldMapper.insert(field);
        return field;
    }

    @Override
    public Map<String, Object> getById(Long id) {
        Field field = fieldMapper.selectById(id);
        if (field == null) return null;

        // 联查当前在种的作物（status=growing）
        List<Crop> crops = cropMapper.selectList(
                new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<Crop>()
                        .eq(Crop::getFieldId, id)
                        .eq(Crop::getStatus, "growing")
                        .orderByDesc(Crop::getCreatedAt));

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("field", field);
        result.put("crops", crops);
        return result;
    }
}
