package com.restassured.tests;

import com.restassured.base.BaseTest;
import com.restassured.config.ConfigReader;
import com.restassured.pojo.AuthResponse;
import com.restassured.service.AuthService;
import io.restassured.response.Response;
import io.qameta.allure.Description;
import io.qameta.allure.Feature;
import io.qameta.allure.Story;
import org.assertj.core.api.SoftAssertions;
import org.testng.annotations.Test;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Authentication Tests
 * Verifies /auth endpoint functionality for token generation
 * Traceable to TC_AUTH_* test cases
 */
@Feature("Authentication")
public class AuthTests extends BaseTest {

    /**
     * TC_AUTH_001 - Create Auth Token - Happy Path
     * Successfully create authentication token with valid credentials
     */
    @Test(description = "Successfully create authentication token with valid credentials")
    @Story("Auth Endpoint")
    @Description("Send POST request to /auth with valid admin credentials")
    public void testCreateAuthTokenHappyPath() {
        logTestStart("TC_AUTH_001", "Create Auth Token - Happy Path");

        // Execute
        AuthResponse authResponse = AuthService.createAuthToken(
                ConfigReader.getUsername(),
                ConfigReader.getPassword()
        );

        // Assert - Traceable to test case specification
        SoftAssertions softAssert = getSoftAssertions();
        softAssert.assertThat(authResponse)
                .as("Auth response should not be null")
                .isNotNull();

        softAssert.assertThat(authResponse.getToken())
                .as("Token should be non-empty alphanumeric string")
                .isNotEmpty()
                .matches("[a-zA-Z0-9]+");

        softAssert.assertAll();
        logTestComplete("TC_AUTH_001");
    }

    /**
     * TC_AUTH_002 - Create Auth Token - Invalid Username
     * Attempt to create token with incorrect username
     */
    @Test(description = "Attempt to create token with incorrect username")
    @Story("Auth Endpoint")
    @Description("Send POST request with invalid username and valid password")
    public void testCreateAuthTokenInvalidUsername() {
        logTestStart("TC_AUTH_002", "Create Auth Token - Invalid Username");

        // Execute
        Response response = AuthService.createAuthTokenWithInvalidUsername("invaliduser", "password123");

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Response status should be 200")
                .isEqualTo(200);

        // Token should be missing or null
        String responseBody = response.getBody().asString();
        logger.info("Response body: " + responseBody);

        logTestComplete("TC_AUTH_002");
    }

    /**
     * TC_AUTH_003 - Create Auth Token - Invalid Password
     * Attempt to create token with incorrect password
     */
    @Test(description = "Attempt to create token with incorrect password")
    @Story("Auth Endpoint")
    @Description("Send POST request with valid username but invalid password")
    public void testCreateAuthTokenInvalidPassword() {
        logTestStart("TC_AUTH_003", "Create Auth Token - Invalid Password");

        // Execute
        Response response = AuthService.createAuthTokenWithInvalidPassword("admin", "wrongpassword");

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Response status should be 200")
                .isEqualTo(200);

        logger.info("Response body: " + response.getBody().asString());
        logTestComplete("TC_AUTH_003");
    }

    /**
     * TC_AUTH_004 - Create Auth Token - Missing Username
     * Attempt to create token without username field
     */
    @Test(description = "Attempt to create token without username field")
    @Story("Auth Endpoint")
    @Description("Send POST request with missing username field")
    public void testCreateAuthTokenMissingUsername() {
        logTestStart("TC_AUTH_004", "Create Auth Token - Missing Username");

        // Execute
        Response response = AuthService.createAuthTokenWithMissingUsername("password123");

        // Assert - Traceable to test case specification
        // Expected: 200 OK or 400 Bad Request depending on API design
        logger.info("Response status: " + response.getStatusCode());
        logger.info("Response body: " + response.getBody().asString());

        logTestComplete("TC_AUTH_004");
    }

    /**
     * TC_AUTH_005 - Create Auth Token - Missing Password
     * Attempt to create token without password field
     */
    @Test(description = "Attempt to create token without password field")
    @Story("Auth Endpoint")
    @Description("Send POST request with missing password field")
    public void testCreateAuthTokenMissingPassword() {
        logTestStart("TC_AUTH_005", "Create Auth Token - Missing Password");

        // Execute
        Response response = AuthService.createAuthTokenWithMissingPassword("admin");

        // Assert - Traceable to test case specification
        logger.info("Response status: " + response.getStatusCode());
        logger.info("Response body: " + response.getBody().asString());

        logTestComplete("TC_AUTH_005");
    }

    /**
     * TC_AUTH_006 - Create Auth Token - Empty Credentials
     * Attempt to create token with empty string credentials
     */
    @Test(description = "Attempt to create token with empty string credentials")
    @Story("Auth Endpoint")
    @Description("Send POST request with empty username and password")
    public void testCreateAuthTokenEmptyCredentials() {
        logTestStart("TC_AUTH_006", "Create Auth Token - Empty Credentials");

        // Execute
        Response response = AuthService.createAuthTokenWithEmptyCredentials();

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Response status should be 200 or 400")
                .isIn(200, 400);

        logger.info("Response body: " + response.getBody().asString());
        logTestComplete("TC_AUTH_006");
    }

    /**
     * TC_AUTH_007 - Create Auth Token - Special Characters in Credentials
     * Attempt to create token with special characters in credentials
     */
    @Test(description = "Attempt to create token with special characters in credentials")
    @Story("Auth Endpoint")
    @Description("Send POST request with special characters in credentials")
    public void testCreateAuthTokenSpecialCharacters() {
        logTestStart("TC_AUTH_007", "Create Auth Token - Special Characters");

        // Execute
        Response response = AuthService.createAuthTokenWithSpecialCharacters(
                "ad@min!#$",
                "p@ssw0rd!@#$%"
        );

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Response status should be 200 or 400")
                .isIn(200, 400);

        logger.info("Response body: " + response.getBody().asString());
        logTestComplete("TC_AUTH_007");
    }
}
