package com.agriculture.service.impl;

import com.agriculture.dto.FarmRequest;
import com.agriculture.entity.Farm;
import com.agriculture.mapper.FarmMapper;
import com.agriculture.service.FarmService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
@RequiredArgsConstructor
public class FarmServiceImpl implements FarmService {

    private final FarmMapper farmMapper;

    @Override
    public List<Farm> listByUser(Long userId) {
        return farmMapper.selectList(
                new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<Farm>()
                        .eq(Farm::getOwnerId, userId));
    }

    @Override
    public Farm create(FarmRequest request, Long userId) {
        Farm farm = new Farm();
        farm.setName(request.getName());
        farm.setAddress(request.getAddress());
        farm.setDescription(request.getDescription());
        farm.setOwnerId(userId);
        farmMapper.insert(farm);
        return farm;
    }
}
