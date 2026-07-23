package com.agriculture.service.impl;

import com.agriculture.service.FileService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import jakarta.annotation.PostConstruct;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

@Service
public class FileServiceImpl implements FileService {

    @Value("${file.upload-dir:uploads}")
    private String uploadDir;

    @PostConstruct
    public void init() {
        try {
            Files.createDirectories(Paths.get(uploadDir));
        } catch (IOException e) {
            throw new RuntimeException("无法创建上传目录: " + uploadDir);
        }
    }

    @Override
    public String upload(MultipartFile file) {
        try {
            return saveFile(file.getBytes(), file.getOriginalFilename());
        } catch (IOException e) {
            throw new RuntimeException("文件上传失败", e);
        }
    }

    @Override
    public String uploadBytes(byte[] bytes, String filename) {
        return saveFile(bytes, filename);
    }

    private String saveFile(byte[] bytes, String originalFilename) {
        String ext = "";
        if (originalFilename != null && originalFilename.contains(".")) {
            ext = originalFilename.substring(originalFilename.lastIndexOf("."));
        }
        String filename = UUID.randomUUID().toString() + ext;
        Path targetPath = Paths.get(uploadDir, filename);
        try {
            Files.write(targetPath, bytes);
            return "/uploads/" + filename;
        } catch (IOException e) {
            throw new RuntimeException("文件保存失败", e);
        }
    }
}
