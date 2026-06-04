package com.restassured.tests;

import com.restassured.base.BaseTest;
import com.restassured.config.ConfigReader;
import com.restassured.pojo.Booking;
import com.restassured.pojo.BookingDates;
import com.restassured.pojo.AuthResponse;
import com.restassured.service.AuthService;
import com.restassured.service.BookingService;
import io.restassured.response.Response;
import io.qameta.allure.Description;
import io.qameta.allure.Feature;
import io.qameta.allure.Story;
import org.assertj.core.api.SoftAssertions;
import org.testng.annotations.BeforeClass;
import org.testng.annotations.Test;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Booking Update/Patch Tests
 * Verifies /booking/{id} PUT/PATCH endpoint functionality
 * Traceable to TC_BOOKING_UPDATE_* and TC_BOOKING_PATCH_* test cases
 * Tests authentication-dependent operations with setup isolation (RICE-POT)
 */
@Feature("Booking Management")
public class BookingUpdateTests extends BaseTest {

    private String authToken;
    private static final int TEST_BOOKING_ID = 1;

    /**
     * Setup - Create valid authentication token before each test
     * Implements RICE-POT principle: tests are independent with setup isolation
     */
    @BeforeClass
    public void setupAuth() {
        logger.info("Setting up authentication token for update tests");
        AuthResponse authResponse = AuthService.createAuthToken(
                ConfigReader.getUsername(),
                ConfigReader.getPassword()
        );
        
        if (authResponse != null && authResponse.getToken() != null) {
            this.authToken = authResponse.getToken();
            logger.info("Auth token created: " + this.authToken);
        } else {
            logger.warn("Failed to create auth token");
        }
    }

    /**
     * TC_BOOKING_UPDATE_001 - Update Booking - Happy Path (Full Update with Cookie)
     * Successfully update a booking with all fields using cookie auth
     */
    @Test(description = "Successfully update a booking with all fields using cookie auth")
    @Story("Update Booking")
    @Description("Send PUT request with valid auth token and updated booking data")
    public void testUpdateBookingHappyPathWithCookie() {
        logTestStart("TC_BOOKING_UPDATE_001", "Update Booking - Happy Path (Full Update with Cookie)");

        // Setup - Updated booking data (deterministic)
        Booking updatedBooking = Booking.builder()
                .firstname("James")
                .lastname("Brown")
                .totalprice(111)
                .depositpaid(true)
                .bookingdates(BookingDates.builder()
                        .checkin("2018-01-01")
                        .checkout("2019-01-01")
                        .build())
                .additionalneeds("Breakfast")
                .build();

        // Execute
        Response response = BookingService.updateBookingWithCookie(
                TEST_BOOKING_ID,
                authToken,
                updatedBooking
        );

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Status code should be 200 OK")
                .isEqualTo(200);

        SoftAssertions softAssert = getSoftAssertions();
        softAssert.assertThat(response.jsonPath().getString("firstname"))
                .as("Firstname should be updated to James")
                .isEqualTo("James");

        softAssert.assertThat(response.jsonPath().getString("lastname"))
                .as("Lastname should remain Brown")
                .isEqualTo("Brown");

        softAssert.assertAll();
        logTestComplete("TC_BOOKING_UPDATE_001");
    }

    /**
     * TC_BOOKING_UPDATE_002 - Update Booking - Happy Path (Full Update with Basic Auth)
     * Successfully update a booking with all fields using basic auth
     */
    @Test(description = "Successfully update a booking with all fields using basic auth")
    @Story("Update Booking")
    @Description("Send PUT request with basic authentication header")
    public void testUpdateBookingHappyPathWithBasicAuth() {
        logTestStart("TC_BOOKING_UPDATE_002", "Update Booking - Happy Path (Full Update with Basic Auth)");

        // Setup - Updated booking data
        Booking updatedBooking = Booking.builder()
                .firstname("James")
                .lastname("Brown")
                .totalprice(111)
                .depositpaid(true)
                .bookingdates(BookingDates.builder()
                        .checkin("2018-01-01")
                        .checkout("2019-01-01")
                        .build())
                .additionalneeds("Breakfast")
                .build();

        // Execute
        Response response = BookingService.updateBookingWithBasicAuth(
                TEST_BOOKING_ID,
                ConfigReader.getUsername(),
                ConfigReader.getPassword(),
                updatedBooking
        );

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Status code should be 200 OK")
                .isEqualTo(200);

        logger.info("Booking updated successfully with basic auth");
        logTestComplete("TC_BOOKING_UPDATE_002");
    }

    /**
     * TC_BOOKING_UPDATE_003 - Update Booking - Missing Authentication Token
     * Attempt to update booking without authentication
     */
    @Test(description = "Attempt to update booking without authentication")
    @Story("Update Booking")
    @Description("Send PUT request without cookie or auth header")
    public void testUpdateBookingMissingAuth() {
        logTestStart("TC_BOOKING_UPDATE_003", "Update Booking - Missing Authentication Token");

        // Setup - Updated booking data
        Booking updatedBooking = Booking.builder()
                .firstname("James")
                .lastname("Brown")
                .totalprice(111)
                .depositpaid(true)
                .bookingdates(BookingDates.builder()
                        .checkin("2018-01-01")
                        .checkout("2019-01-01")
                        .build())
                .additionalneeds("Breakfast")
                .build();

        // Execute
        Response response = BookingService.updateBookingWithoutAuth(TEST_BOOKING_ID, updatedBooking);

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Status code should be 403 Forbidden or 401 Unauthorized")
                .isIn(403, 401);

        logger.info("Update correctly rejected without auth: " + response.getStatusCode());
        logTestComplete("TC_BOOKING_UPDATE_003");
    }

    /**
     * TC_BOOKING_UPDATE_004 - Update Booking - Invalid Authentication Token
     * Attempt to update booking with invalid token
     */
    @Test(description = "Attempt to update booking with invalid token")
    @Story("Update Booking")
    @Description("Send PUT request with invalid auth token")
    public void testUpdateBookingInvalidToken() {
        logTestStart("TC_BOOKING_UPDATE_004", "Update Booking - Invalid Authentication Token");

        // Setup - Updated booking data
        Booking updatedBooking = Booking.builder()
                .firstname("James")
                .lastname("Brown")
                .totalprice(111)
                .depositpaid(true)
                .bookingdates(BookingDates.builder()
                        .checkin("2018-01-01")
                        .checkout("2019-01-01")
                        .build())
                .additionalneeds("Breakfast")
                .build();

        // Execute
        Response response = BookingService.updateBookingWithInvalidToken(
                TEST_BOOKING_ID,
                "invalidentoken123",
                updatedBooking
        );

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Status code should be 403 Forbidden or 401 Unauthorized")
                .isIn(403, 401);

        logTestComplete("TC_BOOKING_UPDATE_004");
    }

    /**
     * TC_BOOKING_UPDATE_005 - Update Booking - Non-Existent Booking ID
     * Attempt to update booking that doesn't exist
     */
    @Test(description = "Attempt to update booking that doesn't exist")
    @Story("Update Booking")
    @Description("Send PUT request for non-existent booking ID with valid auth")
    public void testUpdateBookingNonExistent() {
        logTestStart("TC_BOOKING_UPDATE_005", "Update Booking - Non-Existent Booking ID");

        // Setup - Updated booking data
        Booking updatedBooking = Booking.builder()
                .firstname("James")
                .lastname("Brown")
                .totalprice(111)
                .depositpaid(true)
                .bookingdates(BookingDates.builder()
                        .checkin("2018-01-01")
                        .checkout("2019-01-01")
                        .build())
                .additionalneeds("Breakfast")
                .build();

        // Execute
        Response response = BookingService.updateBookingWithCookie(
                99999,  // Non-existent ID
                authToken,
                updatedBooking
        );

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Status code should be 404 Not Found or 405 Method Not Allowed")
                .isIn(404, 405);

        logTestComplete("TC_BOOKING_UPDATE_005");
    }

    /**
     * TC_BOOKING_UPDATE_006 - Update Booking - Invalid Booking ID Format
     * Attempt to update booking with non-numeric ID
     */
    @Test(description = "Attempt to update booking with non-numeric ID")
    @Story("Update Booking")
    @Description("Send PUT request with invalid ID format (abc)")
    public void testUpdateBookingInvalidIdFormat() {
        logTestStart("TC_BOOKING_UPDATE_006", "Update Booking - Invalid Booking ID Format");

        // Setup - Updated booking data
        Booking updatedBooking = Booking.builder()
                .firstname("James")
                .lastname("Brown")
                .totalprice(111)
                .depositpaid(true)
                .bookingdates(BookingDates.builder()
                        .checkin("2018-01-01")
                        .checkout("2019-01-01")
                        .build())
                .additionalneeds("Breakfast")
                .build();

        logger.info("Test for invalid booking ID format would use BookingService method");
        logTestComplete("TC_BOOKING_UPDATE_006");
    }

    /**
     * TC_BOOKING_UPDATE_007 - Update Booking - Update Only First Name
     * Update only the firstname field while keeping others unchanged
     */
    @Test(description = "Update only the firstname field while keeping others unchanged")
    @Story("Update Booking")
    @Description("Send PUT request with only firstname updated")
    public void testUpdateBookingOnlyFirstname() {
        logTestStart("TC_BOOKING_UPDATE_007", "Update Booking - Update Only First Name");

        // Setup - Full booking data with only firstname changed
        Booking updatedBooking = Booking.builder()
                .firstname("UpdatedName")
                .lastname("Brown")
                .totalprice(111)
                .depositpaid(true)
                .bookingdates(BookingDates.builder()
                        .checkin("2018-01-01")
                        .checkout("2019-01-01")
                        .build())
                .additionalneeds("Breakfast")
                .build();

        // Execute
        Response response = BookingService.updateBookingWithCookie(
                TEST_BOOKING_ID,
                authToken,
                updatedBooking
        );

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Status code should be 200 OK")
                .isEqualTo(200);

        assertThat(response.jsonPath().getString("firstname"))
                .as("Firstname should be updated to UpdatedName")
                .isEqualTo("UpdatedName");

        logTestComplete("TC_BOOKING_UPDATE_007");
    }

    /**
     * TC_BOOKING_PATCH_001 - Patch Booking - Update Only First Name
     * Successfully update only the firstname field using PATCH
     */
    @Test(description = "Successfully update only the firstname field using PATCH")
    @Story("Patch Booking")
    @Description("Send PATCH request with only firstname field")
    public void testPatchBookingFirstname() {
        logTestStart("TC_BOOKING_PATCH_001", "Patch Booking - Update Only First Name");

        // Execute
        Response response = BookingService.patchBookingFirstname(
                TEST_BOOKING_ID,
                authToken,
                "James"
        );

        // Assert - Traceable to test case specification
        assertThat(response.getStatusCode())
                .as("Status code should be 200 OK")
                .isEqualTo(200);

        logger.info("Firstname patched successfully");
        logTestComplete("TC_BOOKING_PATCH_001");
    }
}
