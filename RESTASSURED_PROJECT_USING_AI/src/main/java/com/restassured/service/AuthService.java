package com.restassured.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.restassured.pojo.AuthRequest;
import com.restassured.pojo.AuthResponse;
import com.restassured.specs.SpecificationBuilder;
import io.restassured.response.Response;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import static io.restassured.RestAssured.given;

/**
 * Authentication Service Layer
 * Handles all /auth endpoint operations
 * Separates authentication logic from test classes
 */
public class AuthService {

    private static final Logger logger = LogManager.getLogger(AuthService.class);
    private static final String AUTH_ENDPOINT = "/auth";
    private static final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Create authentication token with given credentials
     * Traceable to TC_AUTH_001
     *
     * @param username Username for authentication
     * @param password Password for authentication
     * @return AuthResponse containing token
     */
    public static AuthResponse createAuthToken(String username, String password) {
        logger.info("Creating auth token for username: " + username);

        AuthRequest authRequest = AuthRequest.builder()
                .username(username)
                .password(password)
                .build();

        Response response = given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .body(authRequest)
                .when()
                .post(AUTH_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();

        logger.info("Auth endpoint response status: " + response.getStatusCode());

        try {
            AuthResponse authResponse = response.as(AuthResponse.class);
            logger.info("Auth token created successfully");
            return authResponse;
        } catch (Exception e) {
            logger.warn("Failed to deserialize auth response: " + e.getMessage());
            return null;
        }
    }

    /**
     * Create authentication token with invalid username
     * Traceable to TC_AUTH_002
     *
     * @param username Invalid username
     * @param password Valid password
     * @return Response object for assertion
     */
    public static Response createAuthTokenWithInvalidUsername(String username, String password) {
        logger.info("Creating auth token with invalid username: " + username);

        AuthRequest authRequest = AuthRequest.builder()
                .username(username)
                .password(password)
                .build();

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .body(authRequest)
                .when()
                .post(AUTH_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Create authentication token with invalid password
     * Traceable to TC_AUTH_003
     *
     * @param username Valid username
     * @param password Invalid password
     * @return Response object for assertion
     */
    public static Response createAuthTokenWithInvalidPassword(String username, String password) {
        logger.info("Creating auth token with invalid password");

        AuthRequest authRequest = AuthRequest.builder()
                .username(username)
                .password(password)
                .build();

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .body(authRequest)
                .when()
                .post(AUTH_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Create authentication token with missing username
     * Traceable to TC_AUTH_004
     *
     * @param password Password value
     * @return Response object for assertion
     */
    public static Response createAuthTokenWithMissingUsername(String password) {
        logger.info("Creating auth token with missing username");

        String jsonBody = "{\"password\": \"" + password + "\"}";

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .body(jsonBody)
                .when()
                .post(AUTH_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Create authentication token with missing password
     * Traceable to TC_AUTH_005
     *
     * @param username Username value
     * @return Response object for assertion
     */
    public static Response createAuthTokenWithMissingPassword(String username) {
        logger.info("Creating auth token with missing password");

        String jsonBody = "{\"username\": \"" + username + "\"}";

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .body(jsonBody)
                .when()
                .post(AUTH_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Create authentication token with empty credentials
     * Traceable to TC_AUTH_006
     *
     * @return Response object for assertion
     */
    public static Response createAuthTokenWithEmptyCredentials() {
        logger.info("Creating auth token with empty credentials");

        AuthRequest authRequest = AuthRequest.builder()
                .username("")
                .password("")
                .build();

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .body(authRequest)
                .when()
                .post(AUTH_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Create authentication token with special characters
     * Traceable to TC_AUTH_007
     *
     * @param username Username with special characters
     * @param password Password with special characters
     * @return Response object for assertion
     */
    public static Response createAuthTokenWithSpecialCharacters(String username, String password) {
        logger.info("Creating auth token with special characters in credentials");

        AuthRequest authRequest = AuthRequest.builder()
                .username(username)
                .password(password)
                .build();

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .body(authRequest)
                .when()
                .post(AUTH_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }
}
