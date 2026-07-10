package com.restassured.pojo;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * POJO representing booking creation/update response
 * Includes bookingid and the booking object
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class BookingResponse {

    @JsonProperty("bookingid")
    private Integer bookingid;

    @JsonProperty("booking")
    private Booking booking;
}
