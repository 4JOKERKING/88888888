package com.agriculture.service;

import com.agriculture.dto.FieldRequest;
import com.agriculture.entity.Field;
import java.util.List;
import java.util.Map;

public interface FieldService {
    List<Field> listByFarm(Long farmId);
    Field create(FieldRequest request);
    Map<String, Object> getById(Long id);
}
