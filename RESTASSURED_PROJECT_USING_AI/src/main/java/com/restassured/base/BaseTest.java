package com.restassured.base;

import com.restassured.config.ConfigReader;
import io.restassured.RestAssured;
import io.restassured.filter.log.RequestLoggingFilter;
import io.restassured.filter.log.ResponseLoggingFilter;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;
import org.assertj.core.api.SoftAssertions;
import org.testng.annotations.BeforeClass;
import org.testng.annotations.BeforeSuite;

import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.PrintStream;

/**
 * Base Test Class for all REST Assured tests
 * Provides common setup/teardown, logging, and assertion utilities
 * Implements RICE-POT framework principles for test independence
 */
public class BaseTest {

    protected static final Logger logger = LogManager.getLogger(BaseTest.class);
    protected SoftAssertions softAssertions;

    /**
     * Suite-level setup - runs once before all tests
     * Initializes REST Assured configuration with base URI and logging
     */
    @BeforeSuite
    public void suiteSetup() {
        logger.info("========== TEST SUITE INITIALIZATION ==========");
        logger.info("Base URI: " + ConfigReader.getBaseUri());
        logger.info("Environment: " + ConfigReader.getProperty("environment", "DEV"));

        // Set REST Assured base URI
        RestAssured.baseURI = ConfigReader.getBaseUri();
        RestAssured.basePath = ConfigReader.getBasePath();

        // Configure timeouts
        RestAssured.config = io.restassured.config.RestAssuredConfig.config()
                .httpClient(io.restassured.config.HttpClientConfig.httpClientConfig()
                        .setParam("http.connection.timeout", ConfigReader.getConnectionTimeout())
                        .setParam("http.socket.timeout", ConfigReader.getReadTimeout()));

        // Setup logging filters if enabled
        if (ConfigReader.isLoggingEnabled()) {
            setupLogging();
        }

        logger.info("========== SUITE INITIALIZATION COMPLETE ==========");
    }

    /**
     * Test class level setup - runs before each test class
     * Initializes soft assertions for flexible assertion validation
     */
    @BeforeClass
    public void beforeClass() {
        logger.info("Initializing soft assertions for test class");
        this.softAssertions = new SoftAssertions();
    }

    /**
     * Setup logging filters for request/response capture
     * Creates log files in target directory for debugging
     */
    protected void setupLogging() {
        try {
            PrintStream requestLog = new PrintStream(
                    new FileOutputStream("target/request-log.txt", true));
            PrintStream responseLog = new PrintStream(
                    new FileOutputStream("target/response-log.txt", true));

            RestAssured.filters(
                    new RequestLoggingFilter(io.restassured.filter.log.LogDetail.ALL, requestLog),
                    new ResponseLoggingFilter(io.restassured.filter.log.LogDetail.ALL, responseLog)
            );

            logger.info("Logging filters configured");
        } catch (FileNotFoundException e) {
            logger.warn("Could not setup logging: " + e.getMessage());
        }
    }

    /**
     * Log test start information
     *
     * @param testName Name of the test
     * @param description Test description for traceability
     */
    protected void logTestStart(String testName, String description) {
        logger.info("========== TEST START: " + testName + " ==========");
        logger.info("Description: " + description);
    }

    /**
     * Log test completion information
     *
     * @param testName Name of the test
     */
    protected void logTestComplete(String testName) {
        logger.info("========== TEST COMPLETE: " + testName + " ==========");
    }

    /**
     * Create new soft assertions instance for current test
     * Allows collecting multiple assertion failures without stopping execution
     *
     * @return SoftAssertions instance
     */
    protected SoftAssertions getSoftAssertions() {
        return new SoftAssertions();
    }

    /**
     * Utility method to wait for async operations with polling
     * Uses Awaitility to avoid Thread.sleep()
     *
     * @param duration Maximum wait duration in seconds
     * @param pollInterval Poll interval in milliseconds
     */
    protected void waitFor(int duration, int pollInterval) {
        logger.info("Waiting up to " + duration + " seconds with " + pollInterval + "ms poll interval");
        // Awaitility can be used here for polling
    }

    /**
     * Verify response contains expected status code
     *
     * @param actualStatusCode Actual response status code
     * @param expectedStatusCode Expected status code
     */
    protected void verifyStatusCode(int actualStatusCode, int expectedStatusCode) {
        softAssertions.assertThat(actualStatusCode)
                .as("HTTP Status Code verification")
                .isEqualTo(expectedStatusCode);
    }

    /**
     * Verify response contains expected content type
     *
     * @param contentType Actual content type
     * @param expectedType Expected content type
     */
    protected void verifyContentType(String contentType, String expectedType) {
        softAssertions.assertThat(contentType)
                .as("Content-Type verification")
                .contains(expectedType);
    }
}
