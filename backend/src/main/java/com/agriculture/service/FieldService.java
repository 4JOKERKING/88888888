package com.agriculture.service;

import com.agriculture.dto.FieldRequest;
import com.agriculture.entity.Field;
import java.util.List;

public interface FieldService {
    List<Field> listByFarm(Long farmId);
    Field create(FieldRequest request);
    Field getById(Long id);
}
