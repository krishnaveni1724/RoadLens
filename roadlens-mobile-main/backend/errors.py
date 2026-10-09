class AnalysisError(Exception):
    def __init__(self, code: str, message: str, *, detail: str | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.detail = detail

    def as_dict(self) -> dict:
        payload = {"success": False, "error": {"code": self.code, "message": self.message}}
        if self.detail:
            payload["error"]["detail"] = self.detail
        return payload
