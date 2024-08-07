from rest_framework_simplejwt.tokens import RefreshToken


class AuthMixin:
    """
    Mixin to handle user authentication-related actions.
    """
    def get_tokens_for_user(self, user):
        """
        Generate JWT tokens for the user.
        """
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
