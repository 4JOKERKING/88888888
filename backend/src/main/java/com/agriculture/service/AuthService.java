package com.agriculture.service;

import com.agriculture.dto.LoginRequest;
import com.agriculture.dto.LoginResponse;
import com.agriculture.dto.RegisterRequest;

public interface AuthService {
    LoginResponse login(LoginRequest request);
    Long register(RegisterRequest request);
}
