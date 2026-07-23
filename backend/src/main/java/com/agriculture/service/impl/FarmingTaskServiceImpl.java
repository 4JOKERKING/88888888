package com.agriculture.service.impl;

import com.agriculture.dto.TaskRequest;
import com.agriculture.dto.TaskStatusRequest;
import com.agriculture.entity.FarmingTask;
import com.agriculture.mapper.FarmingTaskMapper;
import com.agriculture.service.FarmingTaskService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
@RequiredArgsConstructor
public class FarmingTaskServiceImpl implements FarmingTaskService {

    private final FarmingTaskMapper taskMapper;

    @Override
    public List<FarmingTask> listByField(Long fieldId, String status) {
        var wrapper = new com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper<FarmingTask>()
                .orderByDesc(FarmingTask::getCreatedAt);
        if (fieldId != null) wrapper.eq(FarmingTask::getFieldId, fieldId);
        if (status != null && !status.isEmpty()) wrapper.eq(FarmingTask::getStatus, status);
        return taskMapper.selectList(wrapper);
    }

    @Override
    public FarmingTask create(TaskRequest request) {
        FarmingTask task = new FarmingTask();
        task.setFieldId(request.getFieldId());
        task.setCropId(request.getCropId());
        task.setTaskType(request.getTaskType());
        task.setDescription(request.getDescription());
        task.setDueDate(request.getDueDate());
        task.setAssignedTo(request.getAssignedTo());
        task.setStatus("pending");
        taskMapper.insert(task);
        return task;
    }

    @Override
    public FarmingTask updateStatus(Long id, TaskStatusRequest request) {
        FarmingTask task = taskMapper.selectById(id);
        if (task == null) throw new RuntimeException("任务不存在");
        task.setStatus(request.getStatus());
        if ("completed".equals(request.getStatus())) {
            task.setCompletedAt(LocalDateTime.now());
        }
        taskMapper.updateById(task);
        return task;
    }
}
