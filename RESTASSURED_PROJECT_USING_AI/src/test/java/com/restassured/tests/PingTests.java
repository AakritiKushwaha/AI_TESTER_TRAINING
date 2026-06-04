package com.restassured.tests;

import com.restassured.base.BaseTest;
import com.restassured.service.BookingService;
import io.restassured.response.Response;
import io.qameta.allure.Description;
import io.qameta.allure.Feature;
import io.qameta.allure.Story;
import org.testng.annotations.Test;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Ping/Health Check Tests
 * Verifies API health and availability
 * Traceable to TC_PING_* test cases
 */
@Feature("Health Check")
public class PingTests extends BaseTest {

    /**
     * TC_PING_001 - Health Check - Happy Path
     * Verify API health check endpoint returns success
     */
    @Test(description = "Verify API health check endpoint returns success")
    @Story("Ping Endpoint")
    @Description("Send GET request to /ping endpoint and verify HTTP 201 Created response")
    public void testHealthCheckHappyPath() {
        logTestStart("TC_PING_001", "Health Check - Happy Path");

        // Execute
        Response response = BookingService.healthCheck();

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Health check should return 201 Created status")
                .isEqualTo(201);

        assertThat(response.getBody().asString())
                .as("Response should contain OK message")
                .contains("Created");

        logger.info("Response time: " + response.getTime() + "ms");
        assertThat(response.getTime())
                .as("Response time should be less than 2000ms")
                .isLessThan(2000);

        logTestComplete("TC_PING_001");
    }

    /**
     * TC_PING_002 - Health Check - Connection Timeout
     * Verify API behavior when connection times out
     */
    @Test(description = "Verify API behavior when connection times out")
    @Story("Ping Endpoint")
    @Description("Configure request timeout to 100ms and send GET request to /ping")
    public void testHealthCheckWithTimeout() {
        logTestStart("TC_PING_002", "Health Check - Connection Timeout");

        // Execute with short timeout - should timeout
        try {
            Response response = BookingService.healthCheckWithTimeout(100);
            logger.info("Request completed with status: " + response.getStatusCode());
        } catch (Exception e) {
            // Expected: timeout exception should be thrown
            logger.info("Timeout exception caught as expected: " + e.getMessage());
            assertThat(e.getMessage())
                    .as("Should contain timeout indication")
                    .containsIgnoringCase("timeout");
        }

        logTestComplete("TC_PING_002");
    }
}
