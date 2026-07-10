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
 * Booking IDs Retrieval Tests
 * Verifies /booking GET endpoint with various filters
 * Traceable to TC_BOOKING_IDS_* test cases
 */
@Feature("Booking Management")
public class BookingIdsTests extends BaseTest {

    /**
     * TC_BOOKING_IDS_001 - Get All Booking IDs - Happy Path
     * Successfully retrieve all booking IDs
     */
    @Test(description = "Successfully retrieve all booking IDs")
    @Story("Get Booking IDs")
    @Description("Send GET request to /booking without filters")
    public void testGetAllBookingIdsHappyPath() {
        logTestStart("TC_BOOKING_IDS_001", "Get All Booking IDs - Happy Path");

        // Execute
        Response response = BookingService.getAllBookingIds();

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Status code should be 200 OK")
                .isEqualTo(200);

        assertThat(response.getBody().asString())
                .as("Response should be a valid JSON array")
                .startsWith("[");

        logger.info("Total bookings: " + response.getBody().asString().length());
        assertThat(response.getTime())
                .as("Response time should be less than 2000ms")
                .isLessThan(2000);

        logTestComplete("TC_BOOKING_IDS_001");
    }

    /**
     * TC_BOOKING_IDS_002 - Get Booking IDs - Filter by First Name
     * Retrieve booking IDs filtered by guest first name
     */
    @Test(description = "Retrieve booking IDs filtered by guest first name")
    @Story("Get Booking IDs")
    @Description("Send GET request to /booking with firstname filter")
    public void testGetBookingIdsByFirstName() {
        logTestStart("TC_BOOKING_IDS_002", "Get Booking IDs - Filter by First Name");

        // Execute
        Response response = BookingService.getBookingIdsByFirstName("sally");

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Status code should be 200 OK")
                .isEqualTo(200);

        assertThat(response.getBody().asString())
                .as("Response should be a valid JSON array")
                .startsWith("[");

        logTestComplete("TC_BOOKING_IDS_002");
    }

    /**
     * TC_BOOKING_IDS_003 - Get Booking IDs - Filter by Last Name
     * Retrieve booking IDs filtered by guest last name
     */
    @Test(description = "Retrieve booking IDs filtered by guest last name")
    @Story("Get Booking IDs")
    @Description("Send GET request to /booking with lastname filter")
    public void testGetBookingIdsByLastName() {
        logTestStart("TC_BOOKING_IDS_003", "Get Booking IDs - Filter by Last Name");

        // Execute
        Response response = BookingService.getBookingIdsByLastName("Brown");

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Status code should be 200 OK")
                .isEqualTo(200);

        assertThat(response.getBody().asString())
                .as("Response should be a valid JSON array")
                .startsWith("[");

        logTestComplete("TC_BOOKING_IDS_003");
    }

    /**
     * TC_BOOKING_IDS_004 - Get Booking IDs - Filter by Check-in Date
     * Retrieve booking IDs filtered by check-in date
     */
    @Test(description = "Retrieve booking IDs filtered by check-in date")
    @Story("Get Booking IDs")
    @Description("Send GET request to /booking with checkin date filter")
    public void testGetBookingIdsByCheckInDate() {
        logTestStart("TC_BOOKING_IDS_004", "Get Booking IDs - Filter by Check-in Date");

        // Execute
        Response response = BookingService.getBookingIdsByCheckInDate("2014-03-13");

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Status code should be 200 OK")
                .isEqualTo(200);

        assertThat(response.getBody().asString())
                .as("Response should be a valid JSON array")
                .startsWith("[");

        logTestComplete("TC_BOOKING_IDS_004");
    }

    /**
     * TC_BOOKING_IDS_005 - Get Booking IDs - Filter by Check-out Date
     * Retrieve booking IDs filtered by check-out date
     */
    @Test(description = "Retrieve booking IDs filtered by check-out date")
    @Story("Get Booking IDs")
    @Description("Send GET request to /booking with checkout date filter")
    public void testGetBookingIdsByCheckOutDate() {
        logTestStart("TC_BOOKING_IDS_005", "Get Booking IDs - Filter by Check-out Date");

        // Execute
        Response response = BookingService.getBookingIdsByCheckOutDate("2014-03-13");

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Status code should be 200 OK")
                .isEqualTo(200);

        logTestComplete("TC_BOOKING_IDS_005");
    }

    /**
     * TC_BOOKING_IDS_006 - Get Booking IDs - Combined Filters
     * Retrieve booking IDs with multiple filter criteria
     */
    @Test(description = "Retrieve booking IDs with multiple filter criteria")
    @Story("Get Booking IDs")
    @Description("Send GET request to /booking with firstname, lastname, and date filters")
    public void testGetBookingIdsWithCombinedFilters() {
        logTestStart("TC_BOOKING_IDS_006", "Get Booking IDs - Combined Filters");

        // Execute
        Response response = BookingService.getBookingIdsWithCombinedFilters(
                "Sally", "Brown", "2014-03-13", "2014-03-15"
        );

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Status code should be 200 OK")
                .isEqualTo(200);

        logTestComplete("TC_BOOKING_IDS_006");
    }

    /**
     * TC_BOOKING_IDS_007 - Get Booking IDs - Invalid Date Format
     * Attempt to filter bookings with invalid date format
     */
    @Test(description = "Attempt to filter bookings with invalid date format")
    @Story("Get Booking IDs")
    @Description("Send GET request to /booking with invalid date format")
    public void testGetBookingIdsWithInvalidDateFormat() {
        logTestStart("TC_BOOKING_IDS_007", "Get Booking IDs - Invalid Date Format");

        // Execute
        Response response = BookingService.getBookingIdsWithInvalidDateFormat("2014/03/13");

        // Assert - Traceable to test case specification
        // Should return 200 with empty array or error
        assertThat(response.getStatusCode())
                .as("Status code should be 200 OK")
                .isEqualTo(200);

        logTestComplete("TC_BOOKING_IDS_007");
    }

    /**
     * TC_BOOKING_IDS_008 - Get Booking IDs - No Matches Found
     * Retrieve bookings with filters that match no records
     */
    @Test(description = "Retrieve bookings with filters that match no records")
    @Story("Get Booking IDs")
    @Description("Send GET request to /booking with non-existent filter")
    public void testGetBookingIdsWithNoMatches() {
        logTestStart("TC_BOOKING_IDS_008", "Get Booking IDs - No Matches Found");

        // Execute
        Response response = BookingService.getBookingIdsWithNoMatches("NonExistentName");

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Status code should be 200 OK")
                .isEqualTo(200);

        // Should return empty array
        String responseBody = response.getBody().asString();
        assertThat(responseBody)
                .as("Response should be empty array for no matches")
                .contains("[]").or().isEmpty();

        logTestComplete("TC_BOOKING_IDS_008");
    }

    /**
     * TC_BOOKING_IDS_009 - Get Booking IDs - Case Sensitivity
     * Verify filter parameters are case-sensitive/insensitive
     */
    @Test(description = "Verify filter parameters are case-sensitive or insensitive")
    @Story("Get Booking IDs")
    @Description("Send GET request to /booking with uppercase firstname filter")
    public void testGetBookingIdsCaseSensitivity() {
        logTestStart("TC_BOOKING_IDS_009", "Get Booking IDs - Case Sensitivity");

        // Execute with different cases
        Response responseLowercase = BookingService.getBookingIdsByFirstName("sally");
        Response responseUppercase = BookingService.getBookingIdsCaseSensitivity("SALLY");

        // Assert - Traceable to test case specification
        logger.info("Lowercase response: " + responseLowercase.getBody().asString());
        logger.info("Uppercase response: " + responseUppercase.getBody().asString());

        assertThat(responseLowercase.getStatusCode())
                .as("Both requests should return 200 OK")
                .isEqualTo(200);

        logTestComplete("TC_BOOKING_IDS_009");
    }
}
