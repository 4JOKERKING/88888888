package com.agriculture.service;

import com.agriculture.dto.FarmRequest;
import com.agriculture.entity.Farm;
import java.util.List;

public interface FarmService {
    List<Farm> listByUser(Long userId);
    Farm create(FarmRequest request, Long userId);
}
