package com.restassured.pojo;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * POJO representing authentication request payload
 * Used for /auth endpoint POST requests
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class AuthRequest {

    @JsonProperty("username")
    private String username;

    @JsonProperty("password")
    private String password;
}
