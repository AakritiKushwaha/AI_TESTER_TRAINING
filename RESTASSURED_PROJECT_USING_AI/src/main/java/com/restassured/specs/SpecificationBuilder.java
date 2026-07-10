package com.restassured.specs;

import com.restassured.config.ConfigReader;
import io.restassured.builder.RequestSpecBuilder;
import io.restassured.builder.ResponseSpecBuilder;
import io.restassured.filter.log.LogDetail;
import io.restassured.filter.log.RequestLoggingFilter;
import io.restassured.filter.log.ResponseLoggingFilter;
import io.restassured.specification.RequestSpecification;
import io.restassured.specification.ResponseSpecification;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.PrintStream;

/**
 * Specifications builder for REST Assured requests and responses
 * Centralizes common headers, authentication, and logging configuration
 * Implements RequestSpecBuilder and ResponseSpecBuilder patterns
 */
public class SpecificationBuilder {

    private static final Logger logger = LogManager.getLogger(SpecificationBuilder.class);

    /**
     * Build base request specification with common headers and configuration
     * Includes content-type, accept headers, timeout, and logging
     *
     * @return RequestSpecification configured with base settings
     */
    public static RequestSpecification getRequestSpecification() {
        RequestSpecBuilder requestSpecBuilder = new RequestSpecBuilder();

        try {
            // Set base URI
            requestSpecBuilder.setBaseUri(ConfigReader.getBaseUri());

            // Set base path if configured
            String basePath = ConfigReader.getBasePath();
            if (!basePath.isEmpty()) {
                requestSpecBuilder.setBasePath(basePath);
            }

            // Set default content type and accept headers
            requestSpecBuilder.setContentType(ConfigReader.getContentType());
            requestSpecBuilder.setAccept(ConfigReader.getContentType());

            // Set timeouts
            requestSpecBuilder.setConfig(io.restassured.config.RestAssuredConfig.config()
                    .httpClient(io.restassured.config.HttpClientConfig.httpClientConfig()
                            .setParam("http.connection.timeout", ConfigReader.getConnectionTimeout())
                            .setParam("http.socket.timeout", ConfigReader.getReadTimeout())));

            // Enable logging if configured
            if (ConfigReader.isLoggingEnabled()) {
                try {
                    PrintStream requestLog = new PrintStream(new FileOutputStream("target/request-log.txt", true));
                    PrintStream responseLog = new PrintStream(new FileOutputStream("target/response-log.txt", true));

                    requestSpecBuilder.addFilter(new RequestLoggingFilter(LogDetail.ALL, requestLog));
                    requestSpecBuilder.addFilter(new ResponseLoggingFilter(LogDetail.ALL, responseLog));
                } catch (FileNotFoundException e) {
                    logger.warn("Could not create log files: " + e.getMessage());
                }
            }

        } catch (Exception e) {
            logger.error("Error building request specification: " + e.getMessage(), e);
            throw new RuntimeException("Failed to build request specification", e);
        }

        return requestSpecBuilder.build();
    }

    /**
     * Build response specification with common assertions
     * Validates response status codes and content type
     *
     * @return ResponseSpecification with common assertions
     */
    public static ResponseSpecification getResponseSpecification() {
        ResponseSpecBuilder responseSpecBuilder = new ResponseSpecBuilder();

        try {
            // Assert content type is JSON by default
            responseSpecBuilder.expectContentType(ConfigReader.getContentType());

            // Log response if validation fails
            responseSpecBuilder.expectStatusCode(200).log().ifValidationFails();

        } catch (Exception e) {
            logger.error("Error building response specification: " + e.getMessage(), e);
            throw new RuntimeException("Failed to build response specification", e);
        }

        return responseSpecBuilder.build();
    }

    /**
     * Build response specification for specific status code
     *
     * @param statusCode Expected HTTP status code
     * @return ResponseSpecification configured for the given status code
     */
    public static ResponseSpecification getResponseSpecificationForStatus(int statusCode) {
        ResponseSpecBuilder responseSpecBuilder = new ResponseSpecBuilder();
        responseSpecBuilder.expectStatusCode(statusCode);
        responseSpecBuilder.log().ifValidationFails();
        return responseSpecBuilder.build();
    }
}
