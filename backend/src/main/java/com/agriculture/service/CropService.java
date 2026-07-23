package com.agriculture.service;

import com.agriculture.dto.CropRequest;
import com.agriculture.dto.CropUpdateRequest;
import com.agriculture.entity.Crop;
import java.util.List;

public interface CropService {
    List<Crop> listByField(Long fieldId);
    Crop create(CropRequest request);
    Crop update(Long id, CropUpdateRequest request);
}
