package com.agriculture.service.impl;

import com.agriculture.dto.FieldRequest;
import com.agriculture.entity.Field;
import com.agriculture.mapper.FieldMapper;
import com.agriculture.service.FieldService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class FieldServiceImpl implements FieldService {

    private final FieldMapper fieldMapper;

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
    public Field getById(Long id) {
        return fieldMapper.selectById(id);
    }
}
