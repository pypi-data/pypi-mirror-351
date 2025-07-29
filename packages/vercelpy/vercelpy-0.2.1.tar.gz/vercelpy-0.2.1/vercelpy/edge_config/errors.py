"""
Error classes for the Vercel Edge Config client.
"""

_PKG_NAME = "vercelpy"

class UnexpectedNetworkError(Exception):
    def __init__(self, res):
        super().__init__(f"{_PKG_NAME}: Unexpected error due to response with status code {res.status_code}")


class EdgeConfigError:
    UNAUTHORIZED = f"{_PKG_NAME}: Unauthorized"
    EDGE_CONFIG_NOT_FOUND = f"{_PKG_NAME}: Edge Config not found" 