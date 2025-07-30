import logging

from thalentfrx.configs.Environment import get_environment_variables
from thalentfrx.helpers.fastapi.AuthHelper import AuthHelper
from thalentfrx.core.services.AuthDto import LoginRequestDto, TokenResponseDto
from thalentfrx.configs.Logger import get_logger

class AuthBaseService:
    # Logger
    logger: logging.Logger = get_logger(__name__)
    uvicorn_logger: logging.Logger = logging.getLogger(
        "uvicorn.error"
    )

    def __init__(self) -> None:
        super().__init__()
        self.env = get_environment_variables()
        self.helper = AuthHelper()

    def _get_token(
            self, identity: str, is_remember: bool
    ) -> TokenResponseDto:
        key = self.env.JWT_TOKEN_SECRET
        if is_remember:
            duration_access = int(
                self.env.JWT_ACCESS_TOKEN_REMEMBER_DURATION_IN_SEC
            )
        else:
            duration_access = int(
                self.env.JWT_ACCESS_TOKEN_DURATION_IN_SEC
            )
        duration_refresh = int(
            self.env.JWT_REFRESH_TOKEN_DURATION_IN_SEC
        )
        # TODO: change scope based on user permission
        access_token = self.helper.encode_token(
            token_type="access",
            identity=identity,
            key=key,
            duration=duration_access,
            scope=["*"],
        )
        refresh_token = self.helper.encode_token(
            token_type="refresh",
            identity=identity,
            key=key,
            duration=duration_refresh,
            scope=["*"],
        )
        token_type = "Bearer"
        return TokenResponseDto(
            access_token=access_token,
            token_type=token_type,
            expires_in=duration_access,
            refresh_token=refresh_token,
            scope="*",
        )

    def login(
            self, dto: LoginRequestDto
    ) -> TokenResponseDto:
        pass

    def refresh_token(
            self, identity: str
    ) -> TokenResponseDto:
        return self._get_token(identity=identity, is_remember=False)