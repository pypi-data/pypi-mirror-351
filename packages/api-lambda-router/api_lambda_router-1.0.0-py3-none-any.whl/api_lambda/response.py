from json import dumps
from typing import Any, Dict, Tuple

ResponseData = Tuple[Dict[str, Any], int]


def create_response(status_code: int, body: Any, cors: bool = False, cors_origin: str = "*") -> Dict[str, Any]:
    """
    Formats the response for AWS API Gateway, with optional CORS support.

    Args:
        status_code (int): HTTP status code (e.g., 200, 404).
        body (Any): JSON-serializable response body.
        cors (bool): Boolean flag to enable or disable CORS headers. Default is False.
        cors_origin (str): Allowed CORS origin if CORS is enabled. Default is '*' (allowing all origins).

    Returns:
        Dict[str, Any]: A formatted response dictionary compatible with AWS API Gateway, 
                        including CORS headers if specified.

    Example:
        >>> response = create_response(200, {"message": "Success"}, cors=True, cors_origin="https://example.com")
        >>> response["statusCode"]
        200
        >>> headers = response["headers"]
        >>> headers["Access-Control-Allow-Origin"]`
        'https://example.com'
    """
    # Base headers for JSON response
    headers = {
        "Content-Type": "application/json"
    }

    if cors:
        # Add CORS headers only if `cors=True`
        headers.update({
            "Access-Control-Allow-Origin": cors_origin,
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        })

    return {
        "statusCode": status_code,
        "body": dumps(body),
        "headers": headers
    }


