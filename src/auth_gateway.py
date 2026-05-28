class AuthGateway:
    """
    [System Under Test] 원격 제어 프로그램의 인증 및 권한 게이트웨이 (v1.0 Mock)
    실제 서비스 로직은 이 클래스의 메서드 내부에서 구현되어야 합니다.
    테스트를 위해 핵심 비즈니스 로직과 분리된 형태로 설계합니다.
    """

    def __init__(self, token: str):
        self.token = token
        self._is_authenticated = self._validate_token(token)

    @staticmethod
    def _validate_token(token: str) -> bool:
        # 실제로는 JWT 파싱 및 만료/서명 검증 로직이 들어갑니다.
        return "valid_" in token and len(token) > 10

    def get_user_role(self) -> str | None:
        if not self._is_authenticated:
            raise PermissionError("Authentication Failed: Invalid or missing token.")
        # 토큰에 포함된 사용자 역할 정보를 파싱한다고 가정합니다.
        return "admin" if "super" in self.token else ("analyst" if "valid_" in self.token else None)

    def access_resource(self, resource_id: str, required_role: str = "guest") -> dict:
        """
        특정 리소스에 접근하는 핵심 로직. RBAC 검증이 필수입니다.
        """
        current_role = self.get_user_role()

        if not current_role:
            raise PermissionError("Authentication Failed: Token could not be verified.")

        # 1. 권한 우회(RBAC) 체크 (가장 중요!)
        if required_role != "guest" and current_role != required_role and current_role != "admin":
             raise PermissionError(f"Authorization Denied: User role '{current_role}' lacks required permission '{required_role}'.")

        # 2. 필수 입력값 체크 (Input Validation)
        if not resource_id or not isinstance(resource_id, str):
            raise ValueError("API Input Error: Resource ID must be a non-empty string.")

        return {
            "status": "success",
            "data": f"Successfully accessed resource {resource_id} with role {current_role}.",
            "audit_log": f"Audit logged for access attempt by user {current_role}"
        }
# End of AuthGateway Mock Definition