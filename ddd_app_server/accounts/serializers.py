# your_app/serializers.py

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed

UserModel = get_user_model()


class EmailCheckRequestSerializer(serializers.Serializer):
    """
    Serializer for the email check request body.
    Defines the expected input structure and validation for the email.
    """
    email = serializers.EmailField(
        required=True,
        help_text="The email address you want to check for existence."
    )
    # To disallow any extra fields not defined in the serializer, you can add Meta class:
    # class Meta:
    #     extra = serializers.Extra.forbid


class EmailCheckResponseSerializer(serializers.Serializer):
    """
    Serializer for the successful email check response.
    Defines the output structure.
    """
    email_used = serializers.BooleanField(
        help_text="True if the email is already associated with an account, False otherwise."
    )


class EmailTokenObtainSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token_class = None  # This will be set by the TokenObtainPairView

    @classmethod
    def get_token(cls, user):
        if cls.token_class is None:
            # This should ideally be set by the view.
            # If not, we default to RefreshToken.
            # Consider raising an error if strictness is required.
            return RefreshToken.for_user(user)
        return cls.token_class.for_user(user)

    def validate(self, attrs):
        email = attrs.get('email')

        if not email:
            # This check is largely covered by serializers.EmailField validation
            raise serializers.ValidationError('Email is required.')

        try:
            # Using case-insensitive lookup for email
            user = UserModel.objects.get(email__iexact=email)
        except UserModel.DoesNotExist:
            raise AuthenticationFailed('No active account found with the given email.')
        except UserModel.MultipleObjectsReturned:
            # This should not happen if your email field has a unique constraint
            raise AuthenticationFailed('Multiple accounts found for this email. Please contact support.')

        if not user.is_active:
            raise AuthenticationFailed('User account is disabled.')

        self.user = user  # Store user on the serializer instance

        refresh = self.get_token(user)

        data = {
            "code": 200,
            "message": "Token obtained successfully.",
            "data": {
                'id': self.user.id,
                'email': self.user.email,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }

        return data