package com.restassured.pojo;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * POJO representing booking dates object
 * Maps to bookingdates JSON structure in API requests/responses
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class BookingDates {

    @JsonProperty("checkin")
    private String checkin;

    @JsonProperty("checkout")
    private String checkout;
}
