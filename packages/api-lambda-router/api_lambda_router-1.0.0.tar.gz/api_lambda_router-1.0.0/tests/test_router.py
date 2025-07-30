import pytest
from unittest.mock import Mock
import json
from typing import Dict, Any, Optional, Tuple

from api_lambda.router import (
    route, lambda_handler, api_handler, match_path, normalize_path,
    extract_path_from_event, find_matching_route, ROUTES
)
from api_lambda.request import HTTPRequest


class TestRouteDecorator:
    """Test the route decorator functionality."""
    
    def setup_method(self) -> None:
        """Clear routes before each test."""
        ROUTES.clear()
    
    def test_single_method_route(self) -> None:
        """Test registering a route with a single HTTP method."""
        @route("/test", methods="GET")
        def test_handler(request: HTTPRequest) -> Dict[str, str]:
            return {"message": "test"}
        
        assert ("/test", "GET") in ROUTES
        assert ROUTES[("/test", "GET")] == test_handler
    
    def test_multiple_methods_route(self) -> None:
        """Test registering a route with multiple HTTP methods."""
        @route("/test", methods=["GET", "POST"])
        def test_handler(request: HTTPRequest) -> Dict[str, str]:
            return {"message": "test"}
        
        assert ("/test", "GET") in ROUTES
        assert ("/test", "POST") in ROUTES
        assert ROUTES[("/test", "GET")] == test_handler
        assert ROUTES[("/test", "POST")] == test_handler
    
    def test_path_normalization(self) -> None:
        """Test that Flask-style paths are normalized to API Gateway style."""
        @route("/users/<id>/posts/<post_id>", methods="GET")
        def test_handler(request: HTTPRequest) -> Dict[str, str]: # type: ignore
            return {"message": "test"}
        
        assert ("/users/{id}/posts/{post_id}", "GET") in ROUTES


class TestPathUtilities:
    """Test path utility functions."""
    
    def test_normalize_path(self) -> None:
        """Test path normalization from Flask to API Gateway style."""
        assert normalize_path("/users/<id>") == "/users/{id}"
        assert normalize_path("/users/{id}") == "/users/{id}"
        assert normalize_path("/users/<id>/posts/<post_id>") == "/users/{id}/posts/{post_id}"
        assert normalize_path("/static") == "/static"
    
    def test_match_path_exact(self) -> None:
        """Test exact path matching."""
        match, params = match_path("/users", "/users")
        assert match is True
        assert params == {}
    
    def test_match_path_with_parameters(self) -> None:
        """Test path matching with parameters."""
        match, params = match_path("/users/{id}", "/users/123")
        assert match is True
        assert params == {"id": "123"}
        
        match, params = match_path("/users/{user_id}/posts/{post_id}", "/users/456/posts/789")
        assert match is True
        assert params == {"user_id": "456", "post_id": "789"}
    
    def test_match_path_no_match(self) -> None:
        """Test path matching failures."""
        match, params = match_path("/users/{id}", "/posts/123")
        assert match is False
        assert params == {}
        
        match, params = match_path("/users/{id}", "/users/123/extra")
        assert match is False
        assert params == {}
    
    def test_extract_path_from_event(self) -> None:
        """Test extracting path from various Lambda event formats."""
        # Standard API Gateway event
        event1: Dict[str, Any] = {"path": "/users/123"}
        assert extract_path_from_event(event1) == "/users/123"
        
        # Proxy integration event
        event2: Dict[str, Any] = {"rawPath": "/api/users/123"}
        assert extract_path_from_event(event2) == "/api/users/123"
        
        # Event with proxy parameter
        event3: Dict[str, Any] = {"pathParameters": {"proxy": "users/123"}}
        assert extract_path_from_event(event3) == "/users/123"
        
        # Fallback case
        event4: Dict[str, Any] = {}
        assert extract_path_from_event(event4) == "/"


class TestRouteMatching:
    """Test route matching and handler finding."""
    
    def setup_method(self) -> None:
        """Clear routes and set up test routes before each test."""
        ROUTES.clear()
        
        @route("/users", methods="GET")
        def list_users(request: HTTPRequest) -> Dict[str, Any]:
            return {"users": []}
        
        @route("/users/{id}", methods=["GET", "PUT"])
        def handle_user(request: HTTPRequest) -> Dict[str, str]:
            return {"user_id": request.path["id"]}
        
        @route("/posts/{post_id}/comments/{comment_id}", methods="GET")
        def get_comment(request: HTTPRequest) -> Dict[str, str]:
            return {"post_id": request.path["post_id"], "comment_id": request.path["comment_id"]}
    
    def test_find_exact_route(self) -> None:
        """Test finding exact route matches."""
        handler, params = find_matching_route("/users", "GET")
        assert handler is not None
        assert params == {}
    
    def test_find_parameterized_route(self) -> None:
        """Test finding routes with parameters."""
        handler, params = find_matching_route("/users/123", "GET")
        assert handler is not None
        assert params == {"id": "123"}
        
        handler, params = find_matching_route("/posts/456/comments/789", "GET")
        assert handler is not None
        assert params == {"post_id": "456", "comment_id": "789"}
    
    def test_method_not_allowed(self) -> None:
        """Test when path exists but method is not allowed."""
        handler, params = find_matching_route("/users", "POST")
        assert handler is None
        assert params == {}
    
    def test_route_not_found(self) -> None:
        """Test when no route matches."""
        handler, params = find_matching_route("/nonexistent", "GET")
        assert handler is None
        assert params == {}


class TestLambdaHandler:
    """Test the main lambda handler functionality."""
    
    def setup_method(self) -> None:
        """Clear routes and set up test routes before each test."""
        ROUTES.clear()
        
        @route("/hello", methods="GET")
        def hello(request: HTTPRequest) -> Dict[str, str]:
            return {"message": "Hello, World!"}
        
        @route("/users/{id}", methods="GET")
        def get_user(request: HTTPRequest) -> Dict[str, str]:
            return {"user_id": request.path["id"], "name": "John Doe"}
        
        @route("/users", methods="POST")
        def create_user(request: HTTPRequest) -> Tuple[Dict[str, Any], int]:
            return {"created": request.body}, 201
        
        @route("/error", methods="GET")
        def error_handler(request: HTTPRequest) -> Dict[str, str]:
            raise ValueError("Test error")
    
    def create_api_gateway_event(
        self, 
        method: str, 
        path: str, 
        body: Optional[str] = None, 
        query_params: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create a mock API Gateway event."""
        return {
            "httpMethod": method,
            "path": path,
            "body": body,
            "queryStringParameters": query_params,
            "headers": headers or {},
            "requestContext": {}
        }
    
    def test_successful_get_request(self) -> None:
        """Test successful GET request handling."""
        event = self.create_api_gateway_event("GET", "/hello")
        context = Mock()
        
        response = lambda_handler(event, context)
        
        assert response["statusCode"] == 200
        assert json.loads(response["body"]) == {"message": "Hello, World!"}
        assert response["headers"]["Content-Type"] == "application/json"
    
    def test_successful_post_request(self) -> None:
        """Test successful POST request with body."""
        event = self.create_api_gateway_event(
            "POST", 
            "/users", 
            body='{"name": "Jane Doe", "email": "jane@example.com"}'
        )
        context = Mock()
        
        response = lambda_handler(event, context)
        
        assert response["statusCode"] == 201
        body = json.loads(response["body"])
        assert body["created"]["name"] == "Jane Doe"
    
    def test_path_parameters(self) -> None:
        """Test path parameter extraction."""
        event = self.create_api_gateway_event("GET", "/users/123")
        context = Mock()
        
        response = lambda_handler(event, context)
        
        assert response["statusCode"] == 200
        body = json.loads(response["body"])
        assert body["user_id"] == "123"
    
    def test_cors_enabled(self) -> None:
        """Test CORS headers when enabled."""
        event = self.create_api_gateway_event("GET", "/hello")
        context = Mock()
        
        response = lambda_handler(event, context, cors=True)
        
        assert "Access-Control-Allow-Origin" in response["headers"]
        assert response["headers"]["Access-Control-Allow-Origin"] == "*"
    
    def test_options_request(self) -> None:
        """Test OPTIONS preflight request."""
        event = self.create_api_gateway_event("OPTIONS", "/hello")
        context = Mock()
        
        response = lambda_handler(event, context, cors=True)
        
        assert response["statusCode"] == 200
        assert "Access-Control-Allow-Methods" in response["headers"]
    
    def test_route_not_found(self) -> None:
        """Test 404 error when route is not found."""
        event = self.create_api_gateway_event("GET", "/nonexistent")
        context = Mock()
        
        response = lambda_handler(event, context)
        
        assert response["statusCode"] == 404
        body = json.loads(response["body"])
        assert body["error"] is True
        assert body["code"] == "NOT_FOUND"
    
    def test_method_not_allowed(self) -> None:
        """Test when path exists but method is not allowed."""
        event = self.create_api_gateway_event("DELETE", "/hello")
        context = Mock()
        
        response = lambda_handler(event, context)
        
        assert response["statusCode"] == 404
    
    def test_invalid_json_body(self) -> None:
        """Test handling of invalid JSON in request body."""
        event = self.create_api_gateway_event("POST", "/users", body="invalid json")
        context = Mock()
        
        response = lambda_handler(event, context)
        
        # Should still process the request, just with empty body
        print(response)
        assert response["statusCode"] == 201
    
    def test_exception_handling(self) -> None:
        """Test exception handling in route handlers."""
        event = self.create_api_gateway_event("GET", "/error")
        context = Mock()
        
        response = lambda_handler(event, context)
        
        assert response["statusCode"] == 500
        body = json.loads(response["body"])
        assert body["error"] is True
        assert body["code"] == "INTERNAL_SERVER_ERROR"
    
    def test_debug_mode_includes_traceback(self) -> None:
        """Test that debug mode includes traceback in error response."""
        event = self.create_api_gateway_event("GET", "/error")
        context = Mock()
        
        response = lambda_handler(event, context, debug=True)
        
        assert response["statusCode"] == 500
        body = json.loads(response["body"])
        assert "traceback" in body
        assert "ValueError: Test error" in body["traceback"]


class TestAPIHandler:
    """Test the convenience API handler function."""
    
    def setup_method(self) -> None:
        """Clear routes and set up test routes before each test."""
        ROUTES.clear()
        
        @route("/test", methods="GET")
        def test_handler(request: HTTPRequest) -> Dict[str, str]:
            return {"message": "test"}
    
    def test_api_handler_defaults(self) -> None:
        """Test API handler with default settings."""
        event: Dict[str, Any] = {
            "httpMethod": "GET",
            "path": "/test",
            "body": None,
            "queryStringParameters": None,
            "headers": {},
            "requestContext": {}
        }
        context = Mock()
        
        response = api_handler(event, context)
        
        assert response["statusCode"] == 200
        assert "Access-Control-Allow-Origin" in response["headers"]  # CORS enabled by default
    
    def test_custom_error_factory(self) -> None:
        """Test custom error response factory."""
        def custom_error_factory(status_code: int, message: str, error_code: str) -> Dict[str, Any]:
            return {
                "success": False,
                "error": {"message": message, "code": error_code, "status": status_code}
            }
        
        event: Dict[str, Any] = {
            "httpMethod": "GET",
            "path": "/nonexistent",
            "body": None,
            "queryStringParameters": None,
            "headers": {},
            "requestContext": {}
        }
        context = Mock()
        
        response = api_handler(event, context, custom_error_factory=custom_error_factory)
        
        assert response["statusCode"] == 404
        body = json.loads(response["body"])
        assert body["success"] is False
        assert body["error"]["status"] == 404


class TestRequestObject:
    """Test HTTPRequest object functionality."""
    
    def test_request_initialization(self) -> None:
        """Test HTTPRequest initialization with various parameters."""
        request = HTTPRequest(
            body={"name": "John"},
            path={"id": "123"},
            query={"filter": "active"},
            headers={"Content-Type": "application/json"},
            context={"user": "authenticated"}
        )
        
        assert request.body == {"name": "John"}
        assert request.path == {"id": "123"}
        assert request.query == {"filter": "active"}
        assert request.headers == {"Content-Type": "application/json"}
        assert request.context == {"user": "authenticated"}
    
    def test_request_defaults(self) -> None:
        """Test HTTPRequest with default empty values."""
        request = HTTPRequest()
        
        assert request.body == {}
        assert request.path == {}
        assert request.query == {}
        assert request.headers == {}
        assert request.context == {}
    
    def test_request_repr(self) -> None:
        """Test HTTPRequest string representation."""
        request = HTTPRequest(body={"test": True})
        repr_str = repr(request)
        
        assert "HTTPRequest" in repr_str
        assert "body={'test': True}" in repr_str


if __name__ == "__main__":
    pytest.main([__file__])