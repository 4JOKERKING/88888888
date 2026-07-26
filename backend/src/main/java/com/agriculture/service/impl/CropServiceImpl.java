package com.agriculture.service.impl;

import com.agriculture.dto.CropRequest;
import com.agriculture.dto.CropUpdateRequest;
import com.agriculture.entity.Crop;
import com.agriculture.mapper.CropMapper;
import com.agriculture.service.CropService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class CropServiceImpl implements CropService {

    private final CropMapper cropMapper;

    @Override
    public List<Crop> listByField(Long fieldId) {
        return cropMapper.selectList(
                new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<Crop>()
                        .eq(Crop::getFieldId, fieldId)
                        .orderByDesc(Crop::getCreatedAt));
    }

    @Override
    public Crop create(CropRequest request) {
        Crop crop = new Crop();
        crop.setFieldId(request.getFieldId());
        crop.setCropType(request.getCropType());
        crop.setVariety(request.getVariety());
        crop.setPlantDate(request.getPlantDate());
        crop.setPlantArea(request.getPlantArea());
        crop.setAreaUnit(request.getAreaUnit());
        crop.setGrowthStage(request.getGrowthStage());
        crop.setStatus("growing");
        crop.setNotes(request.getNotes());
        cropMapper.insert(crop);
        return crop;
    }

    @Override
    public Crop update(Long id, CropUpdateRequest request) {
        Crop crop = cropMapper.selectById(id);
        if (crop == null) throw new RuntimeException("作物记录不存在");
        if (request.getGrowthStage() != null) crop.setGrowthStage(request.getGrowthStage());
        if (request.getStatus() != null) crop.setStatus(request.getStatus());
        cropMapper.updateById(crop);
        return crop;
    }
}
