package com.restassured.service;

import com.restassured.pojo.Booking;
import com.restassured.pojo.BookingDates;
import com.restassured.pojo.BookingResponse;
import com.restassured.specs.SpecificationBuilder;
import io.restassured.response.Response;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.util.HashMap;
import java.util.Map;

import static io.restassured.RestAssured.given;

/**
 * Booking Service Layer
 * Handles all /booking endpoint operations
 * Separates booking logic from test classes following Service Layer pattern
 */
public class BookingService {

    private static final Logger logger = LogManager.getLogger(BookingService.class);
    private static final String BOOKING_ENDPOINT = "/booking";

    // ==================== PING ENDPOINT ====================

    /**
     * Health check - verify API is running
     * Traceable to TC_PING_001
     *
     * @return Response from ping endpoint
     */
    public static Response healthCheck() {
        logger.info("Performing health check on ping endpoint");

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .when()
                .get("/ping")
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Health check with timeout simulation
     * Traceable to TC_PING_002
     *
     * @param timeoutMs Timeout in milliseconds
     * @return Response from ping endpoint
     */
    public static Response healthCheckWithTimeout(int timeoutMs) {
        logger.info("Performing health check with " + timeoutMs + "ms timeout");

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .socketTimeout(timeoutMs)
                .when()
                .get("/ping")
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    // ==================== GET BOOKING IDS ENDPOINTS ====================

    /**
     * Get all booking IDs
     * Traceable to TC_BOOKING_IDS_001
     *
     * @return Response with booking IDs array
     */
    public static Response getAllBookingIds() {
        logger.info("Retrieving all booking IDs");

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .when()
                .get(BOOKING_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Get booking IDs filtered by first name
     * Traceable to TC_BOOKING_IDS_002
     *
     * @param firstname First name filter
     * @return Response with filtered booking IDs
     */
    public static Response getBookingIdsByFirstName(String firstname) {
        logger.info("Retrieving booking IDs filtered by firstname: " + firstname);

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .queryParam("firstname", firstname)
                .when()
                .get(BOOKING_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Get booking IDs filtered by last name
     * Traceable to TC_BOOKING_IDS_003
     *
     * @param lastname Last name filter
     * @return Response with filtered booking IDs
     */
    public static Response getBookingIdsByLastName(String lastname) {
        logger.info("Retrieving booking IDs filtered by lastname: " + lastname);

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .queryParam("lastname", lastname)
                .when()
                .get(BOOKING_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Get booking IDs filtered by check-in date
     * Traceable to TC_BOOKING_IDS_004
     *
     * @param checkinDate Check-in date in YYYY-MM-DD format
     * @return Response with filtered booking IDs
     */
    public static Response getBookingIdsByCheckInDate(String checkinDate) {
        logger.info("Retrieving booking IDs filtered by checkin date: " + checkinDate);

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .queryParam("checkin", checkinDate)
                .when()
                .get(BOOKING_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Get booking IDs filtered by check-out date
     * Traceable to TC_BOOKING_IDS_005
     *
     * @param checkoutDate Check-out date in YYYY-MM-DD format
     * @return Response with filtered booking IDs
     */
    public static Response getBookingIdsByCheckOutDate(String checkoutDate) {
        logger.info("Retrieving booking IDs filtered by checkout date: " + checkoutDate);

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .queryParam("checkout", checkoutDate)
                .when()
                .get(BOOKING_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Get booking IDs with combined filters
     * Traceable to TC_BOOKING_IDS_006
     *
     * @param firstname First name filter
     * @param lastname Last name filter
     * @param checkinDate Check-in date filter
     * @param checkoutDate Check-out date filter
     * @return Response with filtered booking IDs
     */
    public static Response getBookingIdsWithCombinedFilters(String firstname, String lastname,
                                                             String checkinDate, String checkoutDate) {
        logger.info("Retrieving booking IDs with combined filters");

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .queryParam("firstname", firstname)
                .queryParam("lastname", lastname)
                .queryParam("checkin", checkinDate)
                .queryParam("checkout", checkoutDate)
                .when()
                .get(BOOKING_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Get booking IDs with invalid date format
     * Traceable to TC_BOOKING_IDS_007
     *
     * @param invalidDate Invalid date format
     * @return Response from invalid date request
     */
    public static Response getBookingIdsWithInvalidDateFormat(String invalidDate) {
        logger.info("Retrieving booking IDs with invalid date format: " + invalidDate);

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .queryParam("checkin", invalidDate)
                .when()
                .get(BOOKING_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Get booking IDs with filter that matches no records
     * Traceable to TC_BOOKING_IDS_008
     *
     * @param firstname Non-existent first name
     * @return Response with empty booking IDs array
     */
    public static Response getBookingIdsWithNoMatches(String firstname) {
        logger.info("Retrieving booking IDs with non-existent filter: " + firstname);

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .queryParam("firstname", firstname)
                .when()
                .get(BOOKING_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Test case sensitivity of filters
     * Traceable to TC_BOOKING_IDS_009
     *
     * @param firstname First name with different case
     * @return Response with potentially case-sensitive results
     */
    public static Response getBookingIdsWithCaseSensitivity(String firstname) {
        logger.info("Retrieving booking IDs testing case sensitivity: " + firstname);

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .queryParam("firstname", firstname)
                .when()
                .get(BOOKING_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    // ==================== GET BOOKING ENDPOINT ====================

    /**
     * Get specific booking by ID
     * Traceable to TC_BOOKING_GET_001
     *
     * @param bookingId Booking ID to retrieve
     * @return Response with booking details
     */
    public static Response getBookingById(int bookingId) {
        logger.info("Retrieving booking with ID: " + bookingId);

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .when()
                .get(BOOKING_ENDPOINT + "/" + bookingId)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Get booking with JSON accept header
     * Traceable to TC_BOOKING_GET_002
     *
     * @param bookingId Booking ID to retrieve
     * @return Response in JSON format
     */
    public static Response getBookingByIdAsJson(int bookingId) {
        logger.info("Retrieving booking " + bookingId + " as JSON");

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .header("Accept", "application/json")
                .when()
                .get(BOOKING_ENDPOINT + "/" + bookingId)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Get booking with XML accept header
     * Traceable to TC_BOOKING_GET_003
     *
     * @param bookingId Booking ID to retrieve
     * @return Response in XML format
     */
    public static Response getBookingByIdAsXml(int bookingId) {
        logger.info("Retrieving booking " + bookingId + " as XML");

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .header("Accept", "application/xml")
                .when()
                .get(BOOKING_ENDPOINT + "/" + bookingId)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Get non-existent booking
     * Traceable to TC_BOOKING_GET_004
     *
     * @param bookingId Non-existent booking ID
     * @return Response (should be 404)
     */
    public static Response getBookingByIdNonExistent(int bookingId) {
        logger.info("Retrieving non-existent booking with ID: " + bookingId);

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .when()
                .get(BOOKING_ENDPOINT + "/" + bookingId)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Get booking with invalid ID format
     * Traceable to TC_BOOKING_GET_005
     *
     * @param bookingId Invalid booking ID format
     * @return Response from invalid request
     */
    public static Response getBookingByIdInvalidFormat(String bookingId) {
        logger.info("Retrieving booking with invalid ID format: " + bookingId);

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .when()
                .get(BOOKING_ENDPOINT + "/" + bookingId)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    // ==================== CREATE BOOKING ENDPOINTS ====================

    /**
     * Create new booking with JSON payload
     * Traceable to TC_BOOKING_CREATE_001
     *
     * @param booking Booking object to create
     * @return Response with created booking ID
     */
    public static Response createBookingJson(Booking booking) {
        logger.info("Creating booking with JSON payload");

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .header("Content-Type", "application/json")
                .header("Accept", "application/json")
                .body(booking)
                .when()
                .post(BOOKING_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Create new booking with XML payload
     * Traceable to TC_BOOKING_CREATE_002
     *
     * @param xmlPayload XML payload string
     * @return Response with created booking
     */
    public static Response createBookingXml(String xmlPayload) {
        logger.info("Creating booking with XML payload");

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .header("Content-Type", "text/xml")
                .header("Accept", "application/xml")
                .body(xmlPayload)
                .when()
                .post(BOOKING_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Create booking without firstname (negative test)
     * Traceable to TC_BOOKING_CREATE_003
     *
     * @param booking Booking without firstname
     * @return Response from invalid request
     */
    public static Response createBookingWithoutFirstname(Booking booking) {
        logger.info("Creating booking without firstname");

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .body(booking)
                .when()
                .post(BOOKING_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Create booking without lastname (negative test)
     * Traceable to TC_BOOKING_CREATE_004
     *
     * @param booking Booking without lastname
     * @return Response from invalid request
     */
    public static Response createBookingWithoutLastname(Booking booking) {
        logger.info("Creating booking without lastname");

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .body(booking)
                .when()
                .post(BOOKING_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Create booking with invalid check-in date format
     * Traceable to TC_BOOKING_CREATE_007
     *
     * @param booking Booking with invalid date format
     * @return Response from invalid request
     */
    public static Response createBookingWithInvalidDateFormat(Booking booking) {
        logger.info("Creating booking with invalid date format");

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .body(booking)
                .when()
                .post(BOOKING_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Create booking with checkout before checkin
     * Traceable to TC_BOOKING_CREATE_008
     *
     * @param booking Booking with invalid date range
     * @return Response from invalid request
     */
    public static Response createBookingWithCheckoutBeforeCheckin(Booking booking) {
        logger.info("Creating booking with checkout before checkin");

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .body(booking)
                .when()
                .post(BOOKING_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Create booking with negative price
     * Traceable to TC_BOOKING_CREATE_009
     *
     * @param booking Booking with negative price
     * @return Response from invalid request
     */
    public static Response createBookingWithNegativePrice(Booking booking) {
        logger.info("Creating booking with negative price");

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .body(booking)
                .when()
                .post(BOOKING_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Create booking with special characters
     * Traceable to TC_BOOKING_CREATE_012
     *
     * @param booking Booking with special characters
     * @return Response with created booking
     */
    public static Response createBookingWithSpecialCharacters(Booking booking) {
        logger.info("Creating booking with special characters in name");

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .body(booking)
                .when()
                .post(BOOKING_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Create booking with unicode characters
     * Traceable to TC_BOOKING_CREATE_013
     *
     * @param booking Booking with unicode characters
     * @return Response with created booking
     */
    public static Response createBookingWithUnicodeCharacters(Booking booking) {
        logger.info("Creating booking with unicode characters");

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .header("Content-Type", "application/json; charset=utf-8")
                .body(booking)
                .when()
                .post(BOOKING_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Create booking with decimal price
     * Traceable to TC_BOOKING_CREATE_014
     *
     * @param booking Booking with decimal price
     * @return Response with created booking
     */
    public static Response createBookingWithDecimalPrice(Booking booking) {
        logger.info("Creating booking with decimal price");

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .body(booking)
                .when()
                .post(BOOKING_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Create booking without optional additional needs
     * Traceable to TC_BOOKING_CREATE_015
     *
     * @param booking Booking without additionalneeds
     * @return Response with created booking
     */
    public static Response createBookingWithoutAdditionalNeeds(Booking booking) {
        logger.info("Creating booking without additional needs");

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .body(booking)
                .when()
                .post(BOOKING_ENDPOINT)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    // ==================== UPDATE BOOKING ENDPOINTS ====================

    /**
     * Update booking with full data using cookie authentication
     * Traceable to TC_BOOKING_UPDATE_001
     *
     * @param bookingId Booking ID to update
     * @param token Authentication token
     * @param booking Updated booking data
     * @return Response with updated booking
     */
    public static Response updateBookingWithCookie(int bookingId, String token, Booking booking) {
        logger.info("Updating booking " + bookingId + " with cookie authentication");

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .header("Content-Type", "application/json")
                .header("Accept", "application/json")
                .cookie("token", token)
                .body(booking)
                .when()
                .put(BOOKING_ENDPOINT + "/" + bookingId)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Update booking with basic authentication
     * Traceable to TC_BOOKING_UPDATE_002
     *
     * @param bookingId Booking ID to update
     * @param username Basic auth username
     * @param password Basic auth password
     * @param booking Updated booking data
     * @return Response with updated booking
     */
    public static Response updateBookingWithBasicAuth(int bookingId, String username, String password, Booking booking) {
        logger.info("Updating booking " + bookingId + " with basic authentication");

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .header("Content-Type", "application/json")
                .header("Accept", "application/json")
                .auth().basic(username, password)
                .body(booking)
                .when()
                .put(BOOKING_ENDPOINT + "/" + bookingId)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Update booking without authentication
     * Traceable to TC_BOOKING_UPDATE_003
     *
     * @param bookingId Booking ID to update
     * @param booking Updated booking data
     * @return Response (should be 403/401)
     */
    public static Response updateBookingWithoutAuth(int bookingId, Booking booking) {
        logger.info("Updating booking " + bookingId + " without authentication");

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .header("Content-Type", "application/json")
                .body(booking)
                .when()
                .put(BOOKING_ENDPOINT + "/" + bookingId)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Update booking with invalid token
     * Traceable to TC_BOOKING_UPDATE_004
     *
     * @param bookingId Booking ID to update
     * @param invalidToken Invalid token
     * @param booking Updated booking data
     * @return Response (should be 403/401)
     */
    public static Response updateBookingWithInvalidToken(int bookingId, String invalidToken, Booking booking) {
        logger.info("Updating booking " + bookingId + " with invalid token");

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .header("Content-Type", "application/json")
                .cookie("token", invalidToken)
                .body(booking)
                .when()
                .put(BOOKING_ENDPOINT + "/" + bookingId)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Patch booking - update only firstname
     * Traceable to TC_BOOKING_PATCH_001
     *
     * @param bookingId Booking ID to patch
     * @param token Authentication token
     * @param firstname New firstname
     * @return Response with patched booking
     */
    public static Response patchBookingFirstname(int bookingId, String token, String firstname) {
        logger.info("Patching booking " + bookingId + " firstname field");

        Map<String, Object> patchData = new HashMap<>();
        patchData.put("firstname", firstname);

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .header("Content-Type", "application/json")
                .cookie("token", token)
                .body(patchData)
                .when()
                .patch(BOOKING_ENDPOINT + "/" + bookingId)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    // ==================== DELETE BOOKING ENDPOINTS ====================

    /**
     * Delete booking with authentication
     * Traceable to TC_BOOKING_DELETE_001
     *
     * @param bookingId Booking ID to delete
     * @param token Authentication token
     * @return Response from delete operation
     */
    public static Response deleteBooking(int bookingId, String token) {
        logger.info("Deleting booking " + bookingId);

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .header("Content-Type", "application/json")
                .cookie("token", token)
                .when()
                .delete(BOOKING_ENDPOINT + "/" + bookingId)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }

    /**
     * Delete booking without authentication
     * Traceable to TC_BOOKING_DELETE_002
     *
     * @param bookingId Booking ID to delete
     * @return Response from delete operation (should be 403/401)
     */
    public static Response deleteBookingWithoutAuth(int bookingId) {
        logger.info("Deleting booking " + bookingId + " without authentication");

        return given()
                .spec(SpecificationBuilder.getRequestSpecification())
                .when()
                .delete(BOOKING_ENDPOINT + "/" + bookingId)
                .then()
                .log().ifValidationFails()
                .extract()
                .response();
    }
}
