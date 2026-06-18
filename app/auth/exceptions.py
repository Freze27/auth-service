class AuthError(Exception):
    def __init__(self, error: str, message: str, status_code: int, details: dict | None = None):
        self.error = error
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class EmailTaken(AuthError):
    def __init__(self):
        super().__init__("conflict", "Email already registered", 409)


class UsernameTaken(AuthError):
    def __init__(self):
        super().__init__("conflict", "Username already taken", 409)


class DepartmentNotFound(AuthError):
    def __init__(self):
        super().__init__("not_found", "Department not found", 404)


class InvalidCredentials(AuthError):
    def __init__(self):
        super().__init__("unauthorized", "Invalid credentials", 401)


class UserInactive(AuthError):
    def __init__(self):
        super().__init__("forbidden", "User account is deactivated", 403)


class InvalidToken(AuthError):
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__("unauthorized", message, 401)
