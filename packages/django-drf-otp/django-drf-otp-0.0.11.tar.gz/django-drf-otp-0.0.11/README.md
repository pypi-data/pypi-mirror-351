# Django DRF OTP

Django DRF OTP enables otp authorization.
This module depends on
[Django Rest Framework](https://www.django-rest-framework.org) module.

## Installation

Add `django_drf_otp` and requirements to your `INSTALLED_APPS` setting.

``` python
INSTALLED_APPS = [
    ...,
    "rest_framework", # Requirement
    "rest_framework.authtoken", # Requirement
    "django_drf_otp",
    ...
]
```

If you're intending to use the base auth API you'll probably also want to
add Django DRF OTP's login and logout views.
Add the following to your root `urls.py` file.

```python
urlpatterns = [
    ...,
    path("api-auth/", include("django_drf_otp.urls")),
    ...
]
```

Django DRF OTP provides two endpoints ``login/``  and
``verify-token/``:

- ``login``: Validates user with given ``USERNAME_FIELD`` and ``password``.
By the default returns a success message.

- ``verify-token``: Validates the otp token with given ``token``.
By the default returns a token
(from Rest Framework's Token<sup>[[link][1]]</sup> model).

And finally run ``python manage.py migrate`` to create models.

## Contents

- [``Settings``](#settings)
- [``ViewSets``](#viewsets)
- [``Strategies``](#strategies)

## Settings

Configuration for Django DRF OTP is all namespaced inside
a single Django setting, named `OTP_SETTINGS`.

For example your project's settings.py file might include something like this:

```python
OTP_SETTINGS = {
    "ENABLE_OTP_AUTHENTICATION": True,
}
```

### Accessing settings

If you need to access the values of REST framework's API settings
in your project, you should use the api_settings object. For example.

```python
from django_drf_otp.settings import otp_settings

print(api_settings.ENABLE_OTP_AUTHORIZATION)
```

## API Reference

### API policy settings

The following settings control the basic API policies.

#### ENABLE_OTP_AUTHENTICATION

Enables or Disables OTP Authorization.

Default: ``True``

#### TOKEN_LENGTH

The default token length to use for otp token creation.

Default: ``True``

#### TOKEN_SECRET

The default token creation secret characters.

Default: ``'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'``

#### DEFAULT_TOKEN_TYPE

The default token type to use for otp token creation.

Default: ``TOTP``

#### TOTP_TOKEN_TTL

The default otp token ttl value.

Default: ``300``

#### EMAIL_CONFIG

A dict of email config that used by otp email template.

Default:

```python
{
    "SUBJECT": _("Verification Token"),
    "TEMPLATE_PATH": "django_drf_otp/email.html",
}
```

- ``SUBJECT``: Subject of email.
- ``TEMPLATE_PATH``: The template used for email body.

## ViewSets

### OTPTokenViewSet

The ``OTPTokenViewSet`` class inherits from Rest Framework's
``GenericViewSet``([link](https://www.django-rest-framework.org/api-guide/viewsets/#genericviewset)).
This viewset provides actions: [``login``](#login), [``verify_token``](#verify_token)
and provides methods: [``get_success_response_data``](#get_success_response_data),
[``get_extra_context_data``](#get_extra_context_data).

```python
from rest_framework import viewsets
from django_drf_otp.services import OTPService
from django_drf_otp.serializers import OTPTokenSerializer, OTPTokenVerifySerializer


class OTPTokenViewSet(viewsets.GenericViewSet):
    permission_classes = (AllowAny,)
    serializer_classes = {
        "login": OTPTokenSerializer,
        "verify_token": OTPTokenVerifySerializer,
    }

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.OTP_ENABLED = otp_settings.ENABLE_OTP_AUTHENTICATION

    def login(self, request: Request, *args, **kwargs):
        ...

    def verify_token(self, request: Request, *args, **kwargs):
        ...

    def get_serializer_class(self, *args, **kwargs) -> Type[serializers.Serializer]:
        ...

    def get_success_response_data(self, validated_data: Dict, **kwargs) -> Dict:
        ...

    def get_extra_context_data(self, request: Request, validated_data: Dict) -> Dict:
        ...
```

### API attributes

#### ``permission_classes``

A tuple. Rest Framework's ``permission_classes``<sup>[[link][2]]</sup>
attribute.

Default:

```python
permission_classes = (AllowAny,)
```

#### ``serializer_classes``

A dict contains the action&serializer pair. This attribute used by ``get_serializer_class``<sup>[[link][3]]</sup>
that returns a serializer according to ``action``<sup>[[link][4]]</sup>.

Default:

```python
serializer_classes = {
    "login": OTPTokenSerializer,
    "verify_token": OTPTokenVerifySerializer,
}
```

### API actions&methods

#### ``login``

This action validates the user and
send a token based on the user's notification preference(Currently only email available)
if [``ENABLE_OTP_AUTHENTICATION``](#enable_otp_authentication) is ``True``,
otherwise a token<sup>[[link][1]]</sup>.
By the default uses ``OTPTokenSerializer`` for validation.

#### ``verify_token``

This action validates the otp token and returns a token<sup>[[link][1]]</sup>
if [``ENABLE_OTP_AUTHENTICATION``](#enable_otp_authentication) is ``True``,
otherwise a error message. By the default uses ``OTPTokenVerifySerializer`` for validation.

>💡 **Note:** If you want to change validation serializer class edit
>[``get_serializer_class``](#get_serializer_class) method or
>[``serializer_classes``](#serializer_classes) attribute.
>For editing responses see [``get_success_response_data``](#get_success_response_data).

#### ``get_serializer_class``

This method is used to decide the serializer class and returns a serializer class.
By the default returns a serializer defined in
[``serializer_classes``](#serializer_classes) with the action<sup>[[link][4]]

Default:

```python
def get_serializer_class(self, *args, **kwargs) -> Type[serializers.Serializer]:
    return self.serializer_classes[self.action]
```

#### ``get_success_response_data``

This method is used to decide the response data to return to the user.
Takes the serializer's validated data is returned by
[``get_serializer_class``](#get_serializer_class) and returns a dict.
By the default returns the success message(``{"message": _("OTP token sent successfully.")}``),
othervise Rest Framework's token(``{"token": token.key}``).

>⚠️ Warning: If you are not override
[``get_success_response_data``](#get_success_response_data) and [``get_extra_context_data``](#get_extra_context_data),
you must provide User object with ``user`` key in your serializer's ``validated_data``

#### ``get_extra_context_data``

This method is returns data used by notifiers.
By the default returns a dict contains ``request`` object and user's ``first_name``,
``last_name`` and ``full_name``.

### Example

```python
from django_drf_otp.viewsets import OTPTokenViewSet
from django_drf_otp.settings import otp_settings
from .serializers import CustomLoginSerializer, CustomTokenVerifySerializer

class LoginViewSet(OTPTokenViewSet):
    def get_serializer_class(self, *args, **kwargs) -> Type[serializers.Serializer]:
        if self.action == "login":
            return CustomLoginSerializer
        else:
            return CustomTokenVerifySerializer

    def get_success_response_data(self, validated_data: Dict, **kwargs) -> Dict:
        if self.action == "login" and otp_settings.ENABLE_OTP_AUTHENTICATION:
            return validated_data
        else:
            token,
            return {"token":}
```

## Strategies

Strategies are used to generate otp tokens with different token algorithms
(only TOTP tokens are available for now).
This module uses ``pyotp`` module for a token creation.

### Class's attributes

#### ``token_type``

A string attribute. It can be one of the values defined in TokenType(defined in ``django_drf_otp.enums``).

### API methods

#### ``generate_token``

A abstract method. This method used to create a otp token.
Returns token string.
If you want to implement a new strategy, must be overrided.

Default (in ``BaseOTPStrategy``):

```python
@abstractmethod
def generate_token(self, extra_secret_chars: Optional[str] = None) -> str:
    NotImplementedError()
```

#### ``verify_token``

This method used to verify a otp token.
Returns ``True`` if the token is verified, otherwise ``False``.
if you want to implement a new strategy, must be overrided.

Default (in ``BaseOTPStrategy``):

```python
@abstractmethod
def verify_token(self, token: str, extra_secret_chars: Optional[str] = None) -> bool:
    NotImplementedError()
```

#### ``generate_token_for_user``

A abstract method. This method used to create a otp token for a user
via ``VerificationToken``(defined in ``django_drf_otp.models``).
If you want to implement a new strategy, must be overrided.

Default (in ``BaseOTPStrategy``):

```python
@abstractmethod
def generate_token_for_user(self, user: AbstractUser) -> VerificationToken:
    NotImplementedError()
```

#### ``create_verification_token``

A static method. This method used to create
a ``VerificationToken`` model instance for user.

Default (in ``BaseOTPStrategy``):

```python
@staticmethod
def create_verification_token(
    user: AbstractUser, token: str,
    token_type: TokenType,
    secret_chars: str,
) -> VerificationToken:
    return VerificationToken.objects.create(
        user=user,
        token=token,
        token_type=token_type,
        secret_chars=secret_chars
    )
```

### ``deactivate_old_verification_tokens``

A static method. This method used to deactivates
user's all ``VerificationToken`` instances excluding given token instance.

Default (in ``BaseOTPStrategy``):

```python
@staticmethod
def deactivate_old_verification_tokens(
    verification_token: VerificationToken
) -> None:
    VerificationToken.objects.filter(user=verification_token.user, is_active=True).exclude(
        id=verification_token.id
    ).update(is_active=False)
```

### Example

You can easily implement a new strategy for your special solutions
(with only defined token_types in ``TokenType`` class).

Then create a new strategy class:

```python
class CustomTOTPStrategy(BaseOTPStrategy):
    token_type = TokenType.TOTP

    def generate_token(self, extra_secret_chars: Optional[str] = None) -> str:
        # <Your code here>
```

[1]: https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication (Rest Framework - Token Authentication)
[2]: https://www.django-rest-framework.org/api-guide/views/#permission_classes (Rest Framework - permission_classes)
[3]: https://www.django-rest-framework.org/api-guide/generic-views/#get_serializer_classself (Rest Framework - get_serializer_class)
[4]: https://www.django-rest-framework.org/api-guide/viewsets/#introspecting-viewset-actions (Rest Framework - Introspecting ViewSet actions)
