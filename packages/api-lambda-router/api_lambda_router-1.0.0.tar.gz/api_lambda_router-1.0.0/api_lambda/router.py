from typing import Callable, Dict, Tuple, Any, Union, cast, Optional, Protocol, List, Literal
from .response import create_response, ResponseData
from json import loads, JSONDecodeError
from .request import HTTPRequest
import traceback
import sys
import re

# Allowed HTTP methods
HTTPMethod = Literal["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]

# Define a protocol for route handler functions
class RouteHandler(Protocol):
    def __call__(self, request: HTTPRequest) -> Union[ResponseData, Dict[str, Any], Any]:
        """Route handler function signature."""
        ...

# Define error response structure
class ErrorResponse(Protocol):
    error: bool
    message: str
    code: str

# Route registry to store paths and their associated handlers
ROUTES: Dict[Tuple[str, str], RouteHandler] = {}

# Default error response factory
def default_error_response(status_code: int, message: str, error_code: str) -> Dict[str, Any]:
    """Default error response factory."""
    return {
        "error": True,
        "message": message,
        "code": error_code
    }

# Global error response factory (can be customized)
_error_response_factory: Callable[[int, str, str], Dict[str, Any]] = default_error_response

def set_error_response_factory(factory: Callable[[int, str, str], Dict[str, Any]]) -> None:
    """
    Set a custom error response factory.
    
    Args:
        factory: Function that takes (status_code, message, error_code) and returns error dict
    """
    global _error_response_factory
    _error_response_factory = factory

def route(
    path: str, 
    methods: Union[HTTPMethod, List[HTTPMethod]] = "GET"
) -> Callable[[RouteHandler], RouteHandler]:
    """
    Decorator to register routes in the ROUTES dictionary.
    Supports both single method and multiple methods.

    Args:
        path (str): The endpoint path (e.g., '/docs', '/docs/<id>', '/docs/{id}').
                   Supports both Flask-style <param> and API Gateway-style {param}.
        methods (Union[HTTPMethod, List[HTTPMethod]]): HTTP method(s) (e.g., 'GET', ['GET', 'POST']).

    Returns:
        Callable[[RouteHandler], RouteHandler]: The decorator function that registers the route.

    Examples:
        >>> @route("/docs", methods="POST")
        ... def create_document(request: HTTPRequest) -> ResponseData:
        ...     return {"message": "Document created"}, 201

        >>> @route("/docs/<id>", methods=["GET", "PUT"])
        ... def handle_document(request: HTTPRequest) -> Dict[str, Any]:
        ...     doc_id = request.path["id"]
        ...     return {"id": doc_id}
    """
    def decorator(func: RouteHandler) -> RouteHandler:
        # Normalize path to use {param} format
        normalized_path = normalize_path(path)
        
        # Handle both single method and list of methods
        method_list = [methods] if isinstance(methods, str) else methods
        
        # Register each method
        for method in method_list:
            ROUTES[(normalized_path, method)] = func
        return func
    return decorator

def normalize_path(path: str) -> str:
    """
    Normalize path to use {param} format consistently.
    Converts Flask-style <param> to API Gateway-style {param}.
    
    Args:
        path (str): Original path with either <param> or {param} format
        
    Returns:
        str: Normalized path with {param} format
        
    Examples:
        >>> normalize_path("/users/<id>/posts/<post_id>")
        '/users/{id}/posts/{post_id}'
        >>> normalize_path("/users/{id}/posts/{post_id}")
        '/users/{id}/posts/{post_id}'
    """
    return re.sub(r'<([^>]+)>', r'{\1}', path)

def extract_path_from_event(event: Dict[str, Any]) -> str:
    """
    Extract the actual path from the Lambda event.
    Handles both API Gateway direct integration and proxy integration.
    
    Args:
        event (Dict[str, Any]): AWS Lambda event
        
    Returns:
        str: Extracted path
    """
    # Try to get path from different event structures
    path: Any = event.get("path")
    if path and isinstance(path, str):
        return str(path)
    
    # Handle proxy integration where path might be in pathParameters or rawPath
    raw_path: Any = event.get("rawPath")
    if raw_path and isinstance(raw_path, str):
        return str(raw_path)
    
    # Handle case where we need to construct path from pathParameters
    path_parameters: Dict[str, Any] = event.get("pathParameters") or {}
    if "proxy" in path_parameters:
        proxy_value: Any = path_parameters["proxy"]
        if isinstance(proxy_value, str):
            return f"/{proxy_value}"
    
    # Fallback to root if no path found
    return "/"

def match_path(route_path: str, actual_path: str) -> Tuple[bool, Dict[str, str]]:
    """
    Matches dynamic paths and extracts path parameters.
    Supports both exact matches and parameterized paths.

    Args:
        route_path (str): Route template path (e.g., '/docs/{id}').
        actual_path (str): Incoming request path.

    Returns:
        Tuple[bool, Dict[str, str]]: Tuple where the first element indicates if paths match
                                     and the second element contains extracted parameters.

    Examples:
        >>> match_path('/docs/{id}', '/docs/123')
        (True, {'id': '123'})
        >>> match_path('/users/{user_id}/posts/{post_id}', '/users/456/posts/789')
        (True, {'user_id': '456', 'post_id': '789'})
    """
    # Handle exact match first
    if route_path == actual_path:
        return True, {}
    
    # Strip leading/trailing slashes and split
    route_parts = [part for part in route_path.strip("/").split("/") if part]
    path_parts = [part for part in actual_path.strip("/").split("/") if part]
    
    # Must have same number of parts
    if len(route_parts) != len(path_parts):
        return False, {}
    
    path_params: Dict[str, str] = {}
    for route_part, path_part in zip(route_parts, path_parts):
        if route_part.startswith("{") and route_part.endswith("}"):
            # Extract parameter name
            param_name = route_part[1:-1]
            path_params[param_name] = path_part
        elif route_part != path_part:
            # Non-parameterized parts must match exactly
            return False, {}
    
    return True, path_params

def find_matching_route(path: str, method: str) -> Tuple[Optional[RouteHandler], Dict[str, str]]:
    """
    Find a matching route handler for the given path and method.
    
    Args:
        path (str): Request path
        method (str): HTTP method
        
    Returns:
        Tuple[Optional[RouteHandler], Dict[str, str]]: Handler and extracted path parameters
    """
    # First try exact match
    exact_key = (path, method)
    if exact_key in ROUTES:
        return ROUTES[exact_key], {}
    
    # Then try pattern matching
    for (route_path, route_method), handler in ROUTES.items():
        if route_method == method:
            match, path_params = match_path(route_path, path)
            if match:
                return handler, path_params
    
    return None, {}

def lambda_handler(
    event: Dict[str, Any], 
    context: Any, 
    cors: bool = False, 
    cors_origin: str = "*",
    debug: bool = False
) -> Dict[str, Any]:
    """
    Main handler to route requests based on path and method, with optional CORS support.
    Supports both API Gateway direct integration and proxy integration.

    Args:
        event (Dict[str, Any]): AWS Lambda event containing request details.
        context (Any): AWS Lambda context object.
        cors (bool): Boolean flag to enable/disable CORS headers globally.
        cors_origin (str): Allowed CORS origin if CORS is enabled (default is "*").
        debug (bool): Include stack trace in error responses (default: False).

    Returns:
        Dict[str, Any]: A formatted response dictionary for AWS API Gateway, with optional CORS headers.

    Examples:
        >>> @route("/hello", methods="GET")
        ... def hello(request: HTTPRequest) -> Dict[str, str]:
        ...     return {"message": "Hello, world!"}
        
        >>> def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        ...     return lambda_handler(event, context, cors=True, debug=True)
    """
    # Extract HTTP method and path from event
    http_method_raw: Any = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method")
    http_method: Optional[str] = http_method_raw if isinstance(http_method_raw, str) else None
    path: str = extract_path_from_event(event)
    
    # Handle preflight OPTIONS request for CORS
    if http_method == "OPTIONS":
        return create_response(200, {}, cors=cors, cors_origin=cors_origin)
    
    # Ensure we have a valid HTTP method
    if not http_method:
        error_response = _error_response_factory(400, "Missing HTTP method", "BAD_REQUEST")
        return create_response(400, error_response, cors=cors, cors_origin=cors_origin)

    # Find matching route
    handler, path_params = find_matching_route(path, http_method)
    
    if handler:
        # Safely parse JSON body with error handling
        body_str_raw: Any = event.get("body", "{}") or "{}"
        body_str: str = body_str_raw if isinstance(body_str_raw, str) else "{}"
        try:
            parsed_body: Dict[str, Any] = loads(body_str)
        except JSONDecodeError:
            parsed_body = {}

        # Create Request object with extracted data
        request_data = HTTPRequest(
            body=parsed_body,
            path=path_params,
            query=event.get("queryStringParameters") or {},
            headers=event.get("headers") or {},
            context=event.get("requestContext", {}).get("authorizer") or {},
            method=cast(HTTPMethod, http_method)
        )

        try:
            # Call the handler function with the Request object
            result: Union[ResponseData, Dict[str, Any]] = handler(request_data)
            
            # Handle different return types from handlers
            if isinstance(result, tuple) and len(result) == 2:
                # ResponseData is (status_code, body) format
                response_body, status_code = result
            else:
                response_body, status_code = result, 200
            
            return create_response(status_code, response_body, cors=cors, cors_origin=cors_origin)
        
        except Exception as e:
            # Capture the full traceback
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_details = traceback.format_exception(exc_type, exc_value, exc_traceback)
            traceback_string = ''.join(traceback_details)
            
            # Log the full traceback
            print("Error processing request:", e)
            print("Traceback:", traceback_string)
            
            # Create error response
            error_response = _error_response_factory(500, "Internal Server Error", "INTERNAL_SERVER_ERROR")
            
            # Add traceback to response if debug mode is enabled
            if debug:
                error_response["traceback"] = traceback_string
            
            return create_response(500, error_response, cors=cors, cors_origin=cors_origin)
    
    # No matching route found
    error_response = _error_response_factory(404, "Resource not found", "NOT_FOUND")
    return create_response(404, error_response, cors=cors, cors_origin=cors_origin)

# Convenience function for API handler with common configurations
def api_handler(
    event: Dict[str, Any], 
    context: Any,
    cors_enabled: bool = True,
    cors_origin: str = "*",
    debug_mode: bool = False,
    custom_error_factory: Optional[Callable[[int, str, str], Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """    
    Args:
        event (Dict[str, Any]): AWS Lambda event
        context (Any): AWS Lambda context
        cors_enabled (bool): Enable CORS headers (default: True)
        cors_origin (str): CORS origin (default: "*")
        debug_mode (bool): Include debug info in errors (default: False)
        custom_error_factory: Custom error response factory
        
    Returns:
        Dict[str, Any]: API Gateway response
        
    Example:
        >>> def custom_errors(status: int, msg: str, code: str) -> Dict[str, Any]:
        ...     return {"success": False, "error": {"message": msg, "code": code}}
        
        >>> def handler(event, context):
        ...     return api_handler(event, context, 
        ...                       debug_mode=True, 
        ...                       custom_error_factory=custom_errors)
    """
    # Set custom error factory if provided
    if custom_error_factory:
        original_factory = _error_response_factory
        set_error_response_factory(custom_error_factory)
        
        try:
            return lambda_handler(event, context, cors=cors_enabled, cors_origin=cors_origin, debug=debug_mode)
        finally:
            # Restore original factory
            set_error_response_factory(original_factory)
    else:
        return lambda_handler(event, context, cors=cors_enabled, cors_origin=cors_origin, debug=debug_mode)