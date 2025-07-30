# DIGIT Client Library

A comprehensive Python client library for interacting with DIGIT (Digital Infrastructure for Governance, Impact & Transformation) services. This library provides easy-to-use interfaces for various DIGIT microservices and APIs.

## Table of Contents
- [Core Components](#core-components)
- [Available Services](#available-services)
- [Models](#models)
- [Basic Usage](#basic-usage)
- [Error Handling](#error-handling)
- [Contributing](#contributing)
- [License](#license)

## Core Components

### APIClient
The base client class that handles all HTTP requests to the DIGIT API.

**Parameters:**
- `base_url`: The API endpoint (default: sandbox.digit.org)
- `auth_token`: Authentication token for API requests

**Methods:**
- `get(endpoint, params=None, stream=False, require_auth=True)`: Make GET requests
- `post(endpoint, json_data=None, data=None, additional_headers=None, params=None, files=None, require_auth=True)`: Make POST requests

### Configuration
The `Config` class manages API settings and authentication.

**Parameters:**
- `API_ENDPOINT`: Base URL for API requests
- `AUTH_TOKEN`: Authentication token

**Methods:**
- `set_auth_token(token)`: Set the authentication token
- `set_api_endpoint(endpoint)`: Set the API endpoint

## Available Services

### Authentication Service
Handles user authentication and session management.

**Methods:**
- `get_auth_token(auth_request)`: Get authentication token
- `update_password_no_login(request_info)`: Update password without login
- `logout(request_info)`: Logout user

### User Service
Manages user operations and profiles.

**Methods:**
- `create_citizen(self, citizen_user: CitizenUser, request_info: Optional[RequestInfo] = None)`: Create a new citizen user
- `get_user_details(self, tenant_id: str, request_info: Optional[RequestInfo] = None)`: Get user details using access token.
- `update_profile(self, user_profile: CitizenUser, request_info: Optional[RequestInfo] = None)`: Update user profile.
- `search_users(search_criteria: UserSearchModel, request_info: Optional[RequestInfo] = None)`: Search for users based on given criteria
- `create_user_no_validate(self, citizen_user: CitizenUser, request_info: Optional[RequestInfo] = None)`: Create a new user without validation
- `update_user_no_validate(self, user_profile: CitizenUser, request_info: Optional[RequestInfo] = None)`: Update a user without validation

**Example Usage:**

```python
from digit_client import RequestConfig, UserService, CitizenUserBuilder, RoleBuilder, UserBuilder

# Initialize configuration
auth_token = "your_access_token"  # Replace with the token you copied from digit_init (refer to Basic Usage)
roles = [
    (RoleBuilder()
        .with_code("CITIZEN")
        .with_name("Citizen")
        .with_tenant_id("pg")
        .build()),
    (RoleBuilder()
        .with_code("EMPLOYEE")
        .with_name("Employee")
        .with_tenant_id("pg")
        .build())
]

# Initialize RequestConfig
RequestConfig.initialize(
    api_id="DIGIT-CLIENT",
    version="1.0.0",
    auth_token=auth_token
)

# Create user service instance
user_service = UserService()

# Create a detailed citizen user
citizen_user = (CitizenUserBuilder()
            .with_user_name("93538222114")
            .with_password("Must@123NK")
            .with_salutation("Ms")
            .with_name("mustak")
            .with_gender("MALE")
            .with_mobile_number("9353822214")
            .with_email("xyz@egovernments.org")
            .with_alt_contact_number("")
            .with_pan("VFGGC5624P")
            .with_aadhaar("96a70")
            .with_permanent_address("Dawakhana")
            .with_permanent_city("Kaikoo")
            .with_permanent_pincode("111111")
            .with_correspondence_city("banglore")
            .with_correspondence_pincode("123456")
            .with_correspondence_address("correAddress")
            .with_active(True)
            .with_dob("08/08/1999")
            .with_locale("en_IN")
            .with_type("CITIZEN")
            .with_signature("")
            .with_account_locked(False)
            .with_father_or_husband_name("Palash")
            .with_blood_group("O_POSITIVE")
            .with_identification_mark("Wears spects")
            .with_photo("a8a6cf1e-c84d-4a0c-b2d5-57ec8711ba25")
            .with_otp_reference("14856")
            .with_tenant_id("POM")
            .with_roles(roles)
            .build())


# Create user without validation
response = user_service.create_user_no_validate(citizen_user)
print("Create Response:", response)

# Update user
update_response = user_service.update_user_no_validate(citizen_user)
print("Update Response:", update_response)
```

### MDMS Service
Handles master data operations.

**Methods:**
- Data retrieval
- Schema management
- Version control
- V1 and V2 API support

### Workflow Service
Manages business processes and workflows.

**Methods:**
- Process instance management
- State transitions
- Document handling
- Business service operations
- SLA management

### File Store Service
Handles file uploads and management.

**Methods:**
- File upload
- File retrieval
- Tag-based operations
- Document management

### Transaction Service
Manages financial transactions.

**Methods:**
- Payment processing
- Transaction status
- Tax calculations
- Receipt generation

### Service Request Service
Handles service requests and complaints.

**Methods:**
- Request creation
- Status updates
- Attribute management
- Search and filtering

### Localization Service
Manages multi-language support.

**Methods:**
- Language management
- Translation handling
- Regional settings

### OTP Service
Handles one-time password operations.

**Methods:**
- OTP generation
- Verification
- Resend functionality

### Report Service
Manages report generation and management.

**Methods:**
- Report creation
- Data aggregation
- Export functionality

### PDF Service
Handles PDF operations.

**Methods:**
- PDF generation
- Document processing
- Template management

### Indexer Service
Manages search and indexing operations.

**Methods:**
- Data indexing
- Search functionality
- Result processing

### URL Shortening Service
Handles URL shortening operations.

**Methods:**
- URL shortening
- Link management
- Analytics

### Encryption Service
Handles data encryption and security.

**Methods:**
- Data encryption
- Decryption
- Key management

### Boundary Service
Manages geographical boundaries.

**Methods:**
- Boundary management
- Location services
- Area calculations

### ID Request Service
Handles identity verification requests.

**Methods:**
- ID verification
- Document validation
- Status tracking

## Models

### Authentication Models
- `AuthenticationRequest`
- `CitizenUser`
- `AuthorizationRequest`
- `AuthorizationRequestBuilder`

### User Models
- `UserBuilder`
- `CitizenUserBuilder`
- `RoleBuilder`

### MDMS Models
- `MDMSRequest`
- `MDMSResponse`
- `MasterData`

### Workflow Models
- `WorkflowRequest`
- `BusinessService`
- `SLA`
- `ActionRequest`

### Service Request Models
- `ServiceRequest`
- `ServiceDefinition`
- `Attribute`

### Localization Models
- `Language`
- `Translation`
- `RegionalSettings`

### OTP Models
- `OTPRequest`
- `OTPResponse`

### Report Models
- `ReportRequest`
- `ReportResponse`

### Request Info Models
- `RequestConfig`
- `RequestInfoBuilder`

#### Overview

The `RequestInfo` class is used to manage metadata required for API requests. There are two types of `RequestInfo` configurations:

1. **Global RequestInfo**: Automatically initialized and reused across the application.
2. **Custom RequestInfo**: Manually created and passed to specific API calls.

#### Initialization
Global `RequestInfo` is initialized using the `RequestConfig.initialize()` method. This setup is typically done once at the application startup.

```python
from digit_client import RequestConfig

RequestConfig.initialize(
    api_id="YOUR_APP_ID",
    ver="1.0.0",
    auth_token="GLOBAL_AUTH_TOKEN",
    user_info={
        "uuid": "user-12345",
        "name": "John Doe",
        "correlation_id": "877vgbnjn3vbn3nrv4hv4v",
        "ts": "242353454566",
        "action": "create",
        "did": "88fds8des7f7sf6fstf6sd67f",
        "key": "87673455ghvfjgfdtgbckdgvc67",
        "msg_id": "boljb5l64bkhb4h5bt54b4jev5rev45hkvhj",
        "request_id": "98ufsdvdg7vfdbf6v6v7dv6xvzffvdxf65",
    }
)
```

#### Usage in API Calls
When using global `RequestInfo`, you don't need to pass it explicitly to service methods. The default configuration will be used automatically.

For explicit usage:

```python
from digit_client import RequestInfoBuilder

request_info = (
    RequestInfoBuilder()
    .with_api_id("YOUR_APP_ID")
    .with_version("1.0.0")
    .with_auth_token("AUTH_TOKEN")
    .with_user_info({
        "uuid": "user-12345",
        "name": "John Doe"
    })
    .with_correlation_id("877vgbnjn3vbn3nrv4hv4v")
    .with_timestamp(242353454566)
    .with_action("create")
    .with_did("88fds8des7f7sf6fstf6sd67f")
    .with_key("87673455ghvfjgfdtgbckdgvc67")
    .with_msg_id("boljb5l64bkhb4h5bt54b4jev5rev45hkvhj")
    .with_requester_id("98ufsdvdg7vfdbf6v6v7dv6xvzffvdxf65")
    .build()
)
```

### Transaction Models
- `Transaction`
- `Payment`
- `Receipt`

### File Store Models
- `File`
- `Document`
- `Tag`

### Boundary Models
- `Boundary`
- `Location`
- `Area`

### ID Request Models
- `IDRequest`
- `Verification`

## Basic Usage

### Step 1: Initialize and Authenticate
First, you need to initialize the DIGIT client and authenticate to get your access token:

```bash
digit_init
```

This command will either register a new user or log in an existing one. After successful authentication, you'll receive an access token. Copy this token as you'll need it for subsequent API calls.

### Step 2: Configure the Client
Once you have your access token, you can configure the client and make API calls:

```python
from digit_client import APIClient, Config
from digit_client.services import AuthenticationService
from digit_client.models.auth import AuthenticationRequest

# Initialize configuration
Config.set_api_endpoint("https://your-digit-instance.org")

# Set the authentication token obtained from digit_init
access_token = "your_access_token"  # Replace with the token you copied from digit_init
Config.set_auth_token(access_token)

# Alternatively, you can set the auth token in RequestInfo for individual requests
from digit_client.models import RequestInfo

request_info = RequestInfo(
    auth_token=access_token,
    api_id="your_api_id",
    ver="1.0",
    did="your_device_id",
    msg_id="your_message_id",
    requester_id="your_requester_id"
)
```

## Error Handling

The library includes custom exceptions for handling various error scenarios:
- `AuthenticationError`: Authentication-related errors
- `APIError`: General API errors
- `ValidationError`: Input validation errors

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.