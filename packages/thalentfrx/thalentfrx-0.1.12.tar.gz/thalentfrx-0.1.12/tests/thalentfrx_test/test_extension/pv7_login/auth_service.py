from thalentfrx.core.services.AuthDto import LoginRequestDto, TokenResponseDto
from thalentfrx.core.services.AuthBaseService import AuthBaseService


class auth_service(AuthBaseService):
    def __init__(self) -> None:
        super().__init__()

    def login(
            self, dto: LoginRequestDto
    ) -> TokenResponseDto:
        return self._get_token(identity=dto.username, is_remember=dto.is_remember)
        # return TokenResponseDto(
        #     access_token="123",
        #     token_type="Bearer",
        #     expires_in=100,
        #     refresh_token="456",
        #     scope="*",
        # )


    def refresh_token(
            self, identity: str
    ) -> TokenResponseDto:
        return self._get_token(identity=identity, is_remember=False)
        # return TokenResponseDto(
        #     access_token="123",
        #     token_type="Bearer",
        #     expires_in=100,
        #     refresh_token="456",
        #     scope="*",
        # )
