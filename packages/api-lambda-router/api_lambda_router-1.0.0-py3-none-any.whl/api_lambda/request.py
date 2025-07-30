from typing import Dict, Any, Literal

class HTTPRequest:
    body: Dict[str, Any]
    path: Dict[str, str]
    query: Dict[str, str]
    headers: Dict[str, str]
    context: Dict[str, Any]
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]
    def __init__(self, 
                 body: Dict[str, Any] = {}, 
                 path: Dict[str, str] = {}, 
                 query: Dict[str, str] = {},
                 headers: Dict[str, str] = {}, 
                 context: Dict[str, Any] = {},
                 method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"] = "GET"):
        """
        Represents an HTTP request structure with common request data fields.
        
        Args:
            body (Dict[str, Any]): Parsed JSON body of the request, defaults to an empty dictionary.
            path (Dict[str, str]): Path parameters extracted from the URL.
            query (Dict[str, str]): Query parameters from the URL.
            headers (Dict[str, str]): HTTP headers from the request.
            context (Dict[str, Any]): Authorization or additional context from the request.
        """
        self.body = body or {}
        self.path = path or {}
        self.query = query or {}
        self.headers = headers or {}
        self.context = context or {}
        self.method = method
    
    def __repr__(self) -> str:
        return f"HTTPRequest(body={self.body}, path={self.path}, query={self.query}, headers={self.headers}, context={self.context}, method={self.method})"
