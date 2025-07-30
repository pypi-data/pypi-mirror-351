from typing import Optional


__version__: str


class AWSAuthenticator:

    def __init__(
        self,
        profile_name: Optional[str] = None,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        session_token: Optional[str] = None,
        sso_url: Optional[str] = None,
        sso_role_name: Optional[str] = None,
        sso_account_id: Optional[str] = None,
        region_name: Optional[str] = None
    ) -> None: ...

    def profile(self): ...

    def iam(self): ...

    def sso(self): ...


def get_params(): ...


def main() -> None: ...
