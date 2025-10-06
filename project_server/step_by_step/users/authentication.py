from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):

  def authenticate(self, request):
    raw_token = request.COOKIES.get('access')
    print(f'Token {raw_token}')

    if not raw_token:
      return None

    validated_token = self.get_validated_token(raw_token)
    print(f'Validated token {validated_token}')
    user = self.get_user(validated_token)
    print(f'Validated user {user}')
    return user, validated_token
