package com.restassured.tests;

import com.restassured.base.BaseTest;
import com.restassured.pojo.Booking;
import com.restassured.service.BookingService;
import io.restassured.response.Response;
import io.qameta.allure.Description;
import io.qameta.allure.Feature;
import io.qameta.allure.Story;
import org.assertj.core.api.SoftAssertions;
import org.testng.annotations.Test;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Booking Retrieval Tests
 * Verifies /booking/{id} GET endpoint functionality
 * Traceable to TC_BOOKING_GET_* test cases
 */
@Feature("Booking Management")
public class BookingGetTests extends BaseTest {

    /**
     * TC_BOOKING_GET_001 - Get Booking - Happy Path
     * Successfully retrieve a specific booking by ID
     */
    @Test(description = "Successfully retrieve a specific booking by ID")
    @Story("Get Booking")
    @Description("Send GET request to /booking/1 and verify booking details")
    public void testGetBookingByIdHappyPath() {
        logTestStart("TC_BOOKING_GET_001", "Get Booking - Happy Path");

        // Execute
        Response response = BookingService.getBookingById(1);

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Status code should be 200 OK")
                .isEqualTo(200);

        // Verify booking object structure
        SoftAssertions softAssert = getSoftAssertions();
        softAssert.assertThat(response.jsonPath().get("firstname"))
                .as("Booking should contain firstname field")
                .isNotNull();

        softAssert.assertThat(response.jsonPath().get("lastname"))
                .as("Booking should contain lastname field")
                .isNotNull();

        softAssert.assertThat(response.jsonPath().get("totalprice"))
                .as("Booking should contain totalprice field")
                .isNotNull();

        softAssert.assertThat(response.jsonPath().get("depositpaid"))
                .as("Booking should contain depositpaid field")
                .isNotNull();

        softAssert.assertThat(response.jsonPath().getMap("bookingdates"))
                .as("Booking should contain bookingdates object")
                .isNotNull()
                .containsKeys("checkin", "checkout");

        softAssert.assertAll();
        logTestComplete("TC_BOOKING_GET_001");
    }

    /**
     * TC_BOOKING_GET_002 - Get Booking - Accept JSON Header
     * Request booking in JSON format explicitly
     */
    @Test(description = "Request booking in JSON format explicitly")
    @Story("Get Booking")
    @Description("Send GET request with Accept header set to application/json")
    public void testGetBookingByIdAsJson() {
        logTestStart("TC_BOOKING_GET_002", "Get Booking - Accept JSON Header");

        // Execute
        Response response = BookingService.getBookingByIdAsJson(1);

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Status code should be 200 OK")
                .isEqualTo(200);

        assertThat(response.getContentType())
                .as("Content-Type should be application/json")
                .contains("application/json");

        logTestComplete("TC_BOOKING_GET_002");
    }

    /**
     * TC_BOOKING_GET_003 - Get Booking - Accept XML Header
     * Request booking in XML format
     */
    @Test(description = "Request booking in XML format")
    @Story("Get Booking")
    @Description("Send GET request with Accept header set to application/xml")
    public void testGetBookingByIdAsXml() {
        logTestStart("TC_BOOKING_GET_003", "Get Booking - Accept XML Header");

        // Execute
        Response response = BookingService.getBookingByIdAsXml(1);

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Status code should be 200 OK")
                .isEqualTo(200);

        assertThat(response.getContentType())
                .as("Content-Type should be application/xml")
                .contains("xml");

        logTestComplete("TC_BOOKING_GET_003");
    }

    /**
     * TC_BOOKING_GET_004 - Get Booking - Non-Existent ID
     * Attempt to retrieve booking with non-existent ID
     */
    @Test(description = "Attempt to retrieve booking with non-existent ID")
    @Story("Get Booking")
    @Description("Send GET request to /booking/99999")
    public void testGetBookingByIdNonExistent() {
        logTestStart("TC_BOOKING_GET_004", "Get Booking - Non-Existent ID");

        // Execute
        Response response = BookingService.getBookingByIdNonExistent(99999);

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Status code should be 404 Not Found")
                .isEqualTo(404);

        logTestComplete("TC_BOOKING_GET_004");
    }

    /**
     * TC_BOOKING_GET_005 - Get Booking - Invalid ID Format
     * Attempt to retrieve booking with non-numeric ID
     */
    @Test(description = "Attempt to retrieve booking with non-numeric ID")
    @Story("Get Booking")
    @Description("Send GET request to /booking/abc")
    public void testGetBookingByIdInvalidFormat() {
        logTestStart("TC_BOOKING_GET_005", "Get Booking - Invalid ID Format");

        // Execute
        Response response = BookingService.getBookingByIdInvalidFormat("abc");

        // Assert - Traceable to test case specification
        // Expected: 400 Bad Request or 404 Not Found
        assertThat(response.getStatusCode())
                .as("Status code should be 400 or 404")
                .isIn(400, 404);

        logTestComplete("TC_BOOKING_GET_005");
    }

    /**
     * TC_BOOKING_GET_006 - Get Booking - Negative ID
     * Attempt to retrieve booking with negative ID
     */
    @Test(description = "Attempt to retrieve booking with negative ID")
    @Story("Get Booking")
    @Description("Send GET request to /booking/-1")
    public void testGetBookingByIdNegative() {
        logTestStart("TC_BOOKING_GET_006", "Get Booking - Negative ID");

        // Execute
        Response response = BookingService.getBookingByIdNonExistent(-1);

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Status code should be 404 or 400")
                .isIn(404, 400);

        logTestComplete("TC_BOOKING_GET_006");
    }

    /**
     * TC_BOOKING_GET_007 - Get Booking - Zero ID
     * Attempt to retrieve booking with ID = 0
     */
    @Test(description = "Attempt to retrieve booking with ID = 0")
    @Story("Get Booking")
    @Description("Send GET request to /booking/0")
    public void testGetBookingByIdZero() {
        logTestStart("TC_BOOKING_GET_007", "Get Booking - Zero ID");

        // Execute
        Response response = BookingService.getBookingByIdNonExistent(0);

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Status code should be 404 or 400")
                .isIn(404, 400);

        logTestComplete("TC_BOOKING_GET_007");
    }

    /**
     * TC_BOOKING_GET_008 - Get Booking - Very Large ID
     * Attempt to retrieve booking with extremely large ID
     */
    @Test(description = "Attempt to retrieve booking with extremely large ID")
    @Story("Get Booking")
    @Description("Send GET request to /booking/9999999999999999")
    public void testGetBookingByIdVeryLarge() {
        logTestStart("TC_BOOKING_GET_008", "Get Booking - Very Large ID");

        // Execute
        Response response = BookingService.getBookingByIdNonExistent(9999999999);

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Status code should be 404 Not Found")
                .isEqualTo(404);

        logTestComplete("TC_BOOKING_GET_008");
    }
}
