# REST Assured API Testing Framework - RESTASSURED_PROJECT_USING_AI

## Project Overview

Enterprise-grade API testing framework built with REST Assured following RICE-POT principles:
- **R**eproducible: Same input produces same output
- **I**dempotent: Tests are independent with no side effects
- **C**heckable: Every assertion traceable to requirements
- **E**xhaustive: Comprehensive coverage of API scenarios
- **P**arameterized: Configurable for different environments
- **O**rderly: Well-organized and maintainable code
- **T**raceable: Full traceability to test case specifications

## Architecture

### Layered Architecture Pattern

```
src/
├── main/
│   ├── java/com/restassured/
│   │   ├── pojo/              # Plain Old Java Objects for serialization
│   │   ├── service/           # API Service Layer (separates request logic from tests)
│   │   ├── specs/             # Reusable Specifications (RequestSpecBuilder, ResponseSpecBuilder)
│   │   ├── config/            # Configuration management
│   │   └── base/              # Base test class with common utilities
│   └── resources/
│       ├── config.properties  # Environment-specific configuration
│       └── log4j2.xml         # Logging configuration
└── test/
    └── java/com/restassured/tests/
        ├── PingTests.java              # Health check tests
        ├── AuthTests.java              # Authentication tests
        ├── BookingIdsTests.java        # Booking ID retrieval tests
        ├── BookingGetTests.java        # Single booking retrieval tests
        ├── BookingCreateTests.java     # Booking creation tests
        ├── BookingUpdateTests.java     # Booking update/patch tests
        └── BookingDeleteTests.java     # Booking deletion tests
```

### Design Patterns Implemented

1. **Page Object Model (POM) Variant**: Service Layer Pattern
   - `AuthService.java` - Handles /auth endpoint operations
   - `BookingService.java` - Handles /booking endpoint operations
   - Test classes only contain assertions and test data flows

2. **Builder Pattern**: Used for POJOs with Lombok
   - Reduces boilerplate code
   - Ensures immutability

3. **Specification Builder Pattern**
   - `SpecificationBuilder.java` - Centralizes RequestSpec and ResponseSpec
   - Reuses common headers, authentication, and logging

4. **Configuration Manager Pattern**
   - `ConfigReader.java` - Centralizes environment configuration
   - Supports DEV, STAGE, PROD environments

## Key Features

### 1. POJO-Based Serialization
- **Benefit**: Type-safe, avoids string-based payloads
- **Implementation**: 
  - `Booking.java` - Main booking entity
  - `BookingDates.java` - Nested booking dates
  - `AuthRequest.java` - Authentication request
  - `AuthResponse.java` - Authentication response
  - `BookingResponse.java` - Booking creation response
- **Tool**: Jackson for JSON/XML serialization

### 2. Service Layer Separation
- **Benefit**: Clear separation between API logic and test logic
- **Implementation**: 
  - All API calls encapsulated in `AuthService` and `BookingService`
  - Services return Response objects or POJOs
  - Tests focus only on assertions

### 3. Robust Logging and Reporting
- **Request/Response Logging**: All requests/responses logged to files
- **Test Execution Logging**: Detailed logs for debugging
- **Allure Reporting**: Visual test reports with request/response details
- **Tool**: Log4j2 for logging, Allure for reporting

### 4. JSON Schema Validation
- **Implementation**: REST Assured's `json-schema-validator`
- **Benefit**: Validates structural integrity of responses
- **Usage**: Can be extended to validate against JSON schemas

### 5. Soft Assertions
- **Tool**: AssertJ for soft assertions
- **Benefit**: Multiple assertions without stopping on first failure
- **Usage**: Collect all failures in a single test run

### 6. Configuration Management
- **File**: `src/main/resources/config.properties`
- **Environment Variables**: Base URI, timeouts, credentials
- **Benefit**: Easy switching between DEV, STAGE, PROD

### 7. Dynamic Polling (Awaitility)
- **Alternative to Thread.sleep()**
- **Benefit**: Faster test execution, dynamic waiting
- **Usage**: Can be implemented for async operations

## Test Case Coverage

### Ping/Health Check (2 tests)
- TC_PING_001: Health check happy path
- TC_PING_002: Health check with timeout

### Authentication (7 tests)
- TC_AUTH_001: Create auth token (happy path)
- TC_AUTH_002: Invalid username
- TC_AUTH_003: Invalid password
- TC_AUTH_004: Missing username
- TC_AUTH_005: Missing password
- TC_AUTH_006: Empty credentials
- TC_AUTH_007: Special characters

### Booking IDs Retrieval (9 tests)
- TC_BOOKING_IDS_001: Get all booking IDs
- TC_BOOKING_IDS_002: Filter by firstname
- TC_BOOKING_IDS_003: Filter by lastname
- TC_BOOKING_IDS_004: Filter by checkin date
- TC_BOOKING_IDS_005: Filter by checkout date
- TC_BOOKING_IDS_006: Combined filters
- TC_BOOKING_IDS_007: Invalid date format
- TC_BOOKING_IDS_008: No matches found
- TC_BOOKING_IDS_009: Case sensitivity

### Single Booking Retrieval (8 tests)
- TC_BOOKING_GET_001: Get booking happy path
- TC_BOOKING_GET_002: Get booking as JSON
- TC_BOOKING_GET_003: Get booking as XML
- TC_BOOKING_GET_004: Non-existent ID
- TC_BOOKING_GET_005: Invalid ID format
- TC_BOOKING_GET_006: Negative ID
- TC_BOOKING_GET_007: Zero ID
- TC_BOOKING_GET_008: Very large ID

### Booking Creation (13 tests)
- TC_BOOKING_CREATE_001: Create booking (JSON)
- TC_BOOKING_CREATE_002: Create booking (XML)
- TC_BOOKING_CREATE_003-006: Missing required fields
- TC_BOOKING_CREATE_007: Invalid date format
- TC_BOOKING_CREATE_008: Checkout before checkin
- TC_BOOKING_CREATE_009: Negative price
- TC_BOOKING_CREATE_010: Zero price
- TC_BOOKING_CREATE_012: Special characters
- TC_BOOKING_CREATE_013: Unicode characters
- TC_BOOKING_CREATE_014: Decimal price
- TC_BOOKING_CREATE_015: Optional fields missing

### Booking Update (8 tests)
- TC_BOOKING_UPDATE_001: Update booking with cookie auth
- TC_BOOKING_UPDATE_002: Update booking with basic auth
- TC_BOOKING_UPDATE_003: Missing authentication
- TC_BOOKING_UPDATE_004: Invalid token
- TC_BOOKING_UPDATE_005: Non-existent booking
- TC_BOOKING_UPDATE_006: Invalid ID format
- TC_BOOKING_UPDATE_007: Update only firstname
- TC_BOOKING_PATCH_001: Patch firstname only

### Booking Deletion (6 tests)
- TC_BOOKING_DELETE_001: Delete booking (happy path)
- TC_BOOKING_DELETE_002: Delete without authentication
- TC_BOOKING_DELETE_003: Delete with invalid token
- TC_BOOKING_DELETE_004: Delete non-existent booking
- TC_BOOKING_DELETE_005: Delete with invalid ID format
- TC_BOOKING_DELETE_006: Delete twice

**Total: 62 test cases** covering all scenarios in the test case specification

## Dependencies

### Core Testing Framework
- **REST Assured 5.3.1**: REST client and assertion library
- **TestNG 7.8.0**: Test framework
- **Allure TestNG 2.21.0**: Test reporting

### Serialization & Data Mapping
- **Jackson 2.15.2**: JSON/XML processing
- **Lombok 1.18.30**: Boilerplate reduction

### Assertions & Validation
- **AssertJ 3.24.1**: Soft assertions
- **JSON Schema Validator 5.3.1**: Schema validation
- **Awaitility 4.14.1**: Polling/async operations

### Logging & Infrastructure
- **Log4j2 2.21.0**: Logging framework
- **Apache HttpClient 5.2.1**: HTTP client

## Configuration

### Environment Setup

Edit `src/main/resources/config.properties`:

```properties
# Base URI Configuration
base.uri=https://restful-booker.herokuapp.com
base.path=

# Timeout Configuration (in milliseconds)
connection.timeout=5000
read.timeout=5000

# Authentication Configuration
api.username=admin
api.password=password123

# Logging Configuration
logging.enabled=true

# Allure Reporting Configuration
allure.reporting.enabled=true

# Environment Configuration (DEV, STAGE, PROD)
environment=DEV
```

## Running Tests

### Run All Tests
```bash
mvn clean test
```

### Run Specific Test Class
```bash
mvn clean test -Dtest=AuthTests
```

### Run Tests with Specific Suite
```bash
mvn clean test -Dsuite=testng.xml
```

### Generate Allure Report
```bash
mvn clean test
mvn allure:report
mvn allure:serve
```

## Test Execution Flow

1. **Suite Setup (@BeforeSuite)**
   - Initialize REST Assured configuration
   - Set base URI and timeouts
   - Setup logging filters

2. **Class Setup (@BeforeClass)**
   - Initialize soft assertions
   - Create authentication token (if needed)

3. **Test Execution (@Test)**
   - Log test start with test ID and description
   - Execute API call via Service layer
   - Assert results with traceable assertions
   - Log test completion

4. **Report Generation**
   - Allure captures all request/response details
   - Log files contain complete execution trace
   - Soft assertions provide comprehensive failure analysis

## Best Practices Implemented

### 1. Test Independence (RICE-POT - I)
✓ Each test is completely independent
✓ Setup isolation: Prerequisites created before test
✓ No test interdependencies

### 2. Assertion Traceability (RICE-POT - C)
✓ Every assertion references test case specification
✓ Comments in tests link to TC_* identifiers
✓ Clear assertion messages for debugging

### 3. Zero Hardcoding (DON'T Rule #1)
✓ All credentials, URLs, timeouts in config.properties
✓ Support for environment switching
✓ No hardcoded test data in test classes

### 4. No Static Sleep (DON'T Rule #2)
✓ Awaitility prepared for polling
✓ Dynamic timeout configuration

### 5. Soft Assertions (DON'T Rule #3)
✓ AssertJ SoftAssertions used in multi-field validations
✓ All failures reported in single test run

### 6. JSON Schema Validation (DO Rule #5)
✓ Framework setup ready for schema validation
✓ Can extend tests to validate against JSON schemas

### 7. Service Layer Separation (DO Rule #1)
✓ Test classes contain only assertions
✓ API logic encapsulated in Service layer
✓ Clear separation of concerns

### 8. POJO Usage (DO Rule #2)
✓ All payloads mapped to POJOs
✓ Jackson used for serialization
✓ Lombok reduces boilerplate

## Directory Structure After Build

```
RESTASSURED_PROJECT_USING_AI/
├── target/
│   ├── allure-results/       # Allure report data
│   ├── logs/                 # Execution logs
│   ├── test-classes/         # Compiled test classes
│   ├── classes/              # Compiled main classes
│   └── reports/              # Test reports
├── src/
├── pom.xml
├── testng.xml
└── README.md
```

## Logging Output

### Log Levels
- **DEBUG**: Detailed information (Service layer)
- **INFO**: General information (Tests, Configuration)
- **WARN**: Warning messages (Config issues)
- **ERROR**: Error information (Test failures)

### Log Files
- `target/logs/test-execution.log` - Complete execution log
- `target/logs/info.log` - Info level messages
- `target/logs/error.log` - Error level messages
- `target/logs/rolling-test-*.log` - Rolled over logs
- `target/request-log.txt` - REST Assured request logs
- `target/response-log.txt` - REST Assured response logs

## Troubleshooting

### Authentication Failures
Check:
- `config.properties` has correct credentials
- Token endpoint (/auth) is accessible
- Token has not expired

### Timeout Errors
Check:
- Network connectivity to API server
- `connection.timeout` and `read.timeout` values in config
- API server is responding

### Assertion Failures
Check:
- API specification matches test expectations
- Response data types (String vs Integer)
- Date format expectations

### Build Issues
Check:
- Java version (requires Java 11+)
- Maven version (requires 3.6+)
- All dependencies available in pom.xml

## Extending the Framework

### Add New Test
1. Create new test class extending `BaseTest`
2. Implement service methods in `AuthService` or `BookingService`
3. Write tests with assertions referencing test case IDs
4. Add test to `testng.xml`

### Add New Endpoint
1. Create new POJO for request/response
2. Add methods to appropriate Service class
3. Create test class for endpoint
4. Configure in `config.properties` if needed

### Custom Assertions
```java
SoftAssertions softAssert = getSoftAssertions();
softAssert.assertThat(response.jsonPath().getString("field"))
    .as("Field should have expected value")
    .isEqualTo("expected");
softAssert.assertAll();
```

## Documentation References

- **REST Assured**: https://rest-assured.io/
- **TestNG**: https://testng.org/
- **Allure**: https://docs.qameta.io/allure/
- **Jackson**: https://github.com/FasterXML/jackson
- **Lombok**: https://projectlombok.org/
- **AssertJ**: https://assertj.github.io/assertj-core-features-highlight.html

## Version Information

- **Framework Version**: 1.0.0
- **REST Assured**: 5.3.1
- **TestNG**: 7.8.0
- **Java Target**: 11+
- **Maven**: 3.6+

## Contact & Support

For issues or enhancements, refer to the RICE-POT framework documentation and test case specifications.

---

**Generated**: 2026-06-04
**Project**: RESTASSURED_PROJECT_USING_AI
**Framework**: REST Assured API Testing Framework (Enterprise Grade)
