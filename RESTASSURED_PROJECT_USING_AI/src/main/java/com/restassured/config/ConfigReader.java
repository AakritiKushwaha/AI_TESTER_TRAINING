package com.restassured.config;

import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

/**
 * Configuration reader for managing environment-specific properties
 * Supports DEV, STAGE, and PROD environments
 * Loads properties from config.properties file
 */
public class ConfigReader {

    private static final Properties properties = new Properties();
    private static final String CONFIG_FILE = "config.properties";

    static {
        loadProperties();
    }

    /**
     * Load properties from config.properties file
     */
    private static void loadProperties() {
        try (InputStream input = ConfigReader.class.getClassLoader().getResourceAsStream(CONFIG_FILE)) {
            if (input == null) {
                throw new RuntimeException("Configuration file not found: " + CONFIG_FILE);
            }
            properties.load(input);
        } catch (IOException e) {
            throw new RuntimeException("Failed to load configuration: " + e.getMessage(), e);
        }
    }

    /**
     * Get configuration value by key
     *
     * @param key Property key
     * @return Property value
     */
    public static String getProperty(String key) {
        String value = properties.getProperty(key);
        if (value == null) {
            throw new RuntimeException("Property not found: " + key);
        }
        return value;
    }

    /**
     * Get configuration value with default fallback
     *
     * @param key         Property key
     * @param defaultValue Default value if key not found
     * @return Property value or default
     */
    public static String getProperty(String key, String defaultValue) {
        return properties.getProperty(key, defaultValue);
    }

    // Configuration accessor methods
    public static String getBaseUri() {
        return getProperty("base.uri");
    }

    public static String getBasePath() {
        return getProperty("base.path", "");
    }

    public static int getConnectionTimeout() {
        return Integer.parseInt(getProperty("connection.timeout", "5000"));
    }

    public static int getReadTimeout() {
        return Integer.parseInt(getProperty("read.timeout", "5000"));
    }

    public static String getContentType() {
        return getProperty("content.type", "application/json");
    }

    public static String getUsername() {
        return getProperty("api.username");
    }

    public static String getPassword() {
        return getProperty("api.password");
    }

    public static boolean isLoggingEnabled() {
        return Boolean.parseBoolean(getProperty("logging.enabled", "true"));
    }

    public static boolean isAllureReportingEnabled() {
        return Boolean.parseBoolean(getProperty("allure.reporting.enabled", "true"));
    }
}
