# API Reference

This document describes the API endpoints available in the Customer Management System. These endpoints are primarily used by the frontend to interact with the backend.

## Authentication

All API endpoints require authentication. The application uses Django's session-based authentication.

### Login

**URL**: `/login/`

**Method**: `POST`

**Request Body**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Response**:
- Success: Redirects to dashboard
- Error: Returns login page with error message

### Logout

**URL**: `/logout/`

**Method**: `GET`

**Response**: Redirects to login page

## Customer Management

### List Customers

**URL**: `/customers/`

**Method**: `GET`

**Query Parameters**:
- `status`: Filter by status
- `search`: Search term for name, phone, or area

**Response**:
- Success: Renders customer list template with customer data
- Error: Returns error message

### Customer Detail

**URL**: `/customers/<uuid:customer_id>/`

**Method**: `GET`

**Response**:
- Success: Renders customer detail template with customer data
- Error: Returns 404 or permission denied

### Update Customer Status

**URL**: `/customers/<uuid:customer_id>/update-status/`

**Method**: `POST`

**Request Body**:
```json
{
  "status": "string",
  "notes": "string"
}
```

**Response**:
- Success:
  ```json
  {
    "success": true,
    "status": "string",
    "status_display": "string"
  }
  ```
- Error:
  ```json
  {
    "error": "error message"
  }
  ```

### Assign Customer

**URL**: `/customers/<uuid:customer_id>/assign/`

**Method**: `POST`

**Request Body**:
```json
{
  "sales_user": "user_id"
}
```

**Response**:
- Success:
  ```json
  {
    "success": true,
    "assigned_to": "username"
  }
  ```
- Error:
  ```json
  {
    "error": "error message"
  }
  ```

## File Import

### Import File

**URL**: `/import/`

**Method**: `POST`

**Request Body**: Multipart form data with file

**Response**:
- Success: Redirects to import history page
- Error: Returns error message

### Import History

**URL**: `/import/history/`

**Method**: `GET`

**Response**: Renders import history template with import data

## Dashboard Data

### Manager Dashboard

**URL**: `/dashboard/manager/`

**Method**: `GET`

**Response**: Renders manager dashboard template with:
- Total customers count
- Assigned/unassigned counts
- Status distribution
- Sales performance data
- Recent imports

### Sales Dashboard

**URL**: `/dashboard/sales/`

**Method**: `GET`

**Response**: Renders sales dashboard template with:
- Assigned customers count
- Status distribution
- Recent activity
- Assigned customers list

## Bulk Operations

### Bulk Assign Customers

**URL**: `/customers/bulk-assign/`

**Method**: `POST`

**Request Body**:
```json
{
  "customer_ids": ["uuid1", "uuid2", ...],
  "sales_user": "user_id"
}
```

**Response**: Redirects to unassigned customers page

### Random Assign Customers

**URL**: `/customers/random-assign/`

**Method**: `POST`

**Request Body**:
```json
{
  "customer_ids": ["uuid1", "uuid2", ...]
}
```

**Response**: Redirects to unassigned customers page

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid input |
| 403 | Forbidden - Permission denied |
| 404 | Not Found - Resource not found |
| 405 | Method Not Allowed - Invalid HTTP method |
| 500 | Internal Server Error |

## Request Examples

### Update Customer Status

```bash
curl -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Cookie: sessionid=your_session_id" \
  -d "status=INTERESTED&notes=Customer showed interest in BCA program" \
  http://localhost:8000/customers/550e8400-e29b-41d4-a716-446655440000/update-status/
```

### Assign Customer

```bash
curl -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Cookie: sessionid=your_session_id" \
  -d "sales_user=1" \
  http://localhost:8000/customers/550e8400-e29b-41d4-a716-446655440000/assign/
```

## Response Examples

### Customer Detail

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "John Smith",
  "phone_number": "9876543210",
  "area": "North Delhi",
  "date": "2025-04-15",
  "status": "INTERESTED",
  "assigned_to": {
    "id": 1,
    "username": "counsellor1"
  },
  "status_history": [
    {
      "previous_status": "VALID",
      "new_status": "INTERESTED",
      "changed_by": "counsellor1",
      "changed_at": "2023-04-10T14:30:00Z",
      "notes": "Customer showed interest in BCA program"
    }
  ]
}
```

### Status Update Response

```json
{
  "success": true,
  "status": "INTERESTED",
  "status_display": "Interested"
}
```

## Notes on API Usage

1. **Authentication**: All API endpoints require authentication. Make sure to include session cookies in your requests.

2. **CSRF Protection**: For POST requests, include the CSRF token either as a cookie or as a form field.

3. **Content Types**: The API primarily accepts form data (`application/x-www-form-urlencoded`) for POST requests.

4. **Error Handling**: Always check for error responses and handle them appropriately.

5. **Permissions**: Different endpoints have different permission requirements based on user roles.

## API Limitations

1. The API is primarily designed for internal use by the application's frontend.

2. There is no formal versioning of the API.

3. Rate limiting is not implemented.

4. Authentication is session-based, not token-based.

## Future API Enhancements

1. RESTful API with proper versioning

2. Token-based authentication

3. Comprehensive API documentation with Swagger/OpenAPI

4. Bulk operations for more endpoints

5. Pagination for list endpoints
