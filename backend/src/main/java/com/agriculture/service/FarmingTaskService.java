package com.agriculture.service;

import com.agriculture.dto.TaskRequest;
import com.agriculture.dto.TaskStatusRequest;
import com.agriculture.entity.FarmingTask;
import java.util.List;

public interface FarmingTaskService {
    List<FarmingTask> listByField(Long fieldId, String status);
    FarmingTask create(TaskRequest request);
    FarmingTask updateStatus(Long id, TaskStatusRequest request);
}
