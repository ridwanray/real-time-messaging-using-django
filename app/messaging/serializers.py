from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Message, User


class CustomObtainTokenPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        access_token = refresh.access_token
        self.user.save_last_login()
        data["refresh"] = str(refresh)
        data["access"] = str(access_token)
        return data

    @classmethod
    def get_token(cls, user: User):
        if not user.is_active:
            raise exceptions.AuthenticationFailed(
                _("Account  deactivated!"), code="authentication"
            )
        token = super().get_token(user)
        token.id = user.id
        token["email"] = user.email
        return token


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128, min_length=4)

    def validate_old_password(self, value):
        request = self.context["request"]

        if not request.user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def save(self):
        user: User = self.context["request"].user
        new_password = self.validated_data["new_password"]
        user.set_password(new_password)
        user.save(update_fields=["password"])


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class OnboardUserSerializer(serializers.Serializer):
    """Serializer for creating user object"""

    email = serializers.EmailField()
    password = serializers.CharField(min_length=4)

    def validate(self, attrs: dict):
        email = attrs.get("email")
        cleaned_email = email.lower().strip()
        if get_user_model().objects.filter(email__iexact=cleaned_email).exists():
            raise serializers.ValidationError({"email": "User exists with this email"})
        return super().validate(attrs)

    def create(self, validated_data: dict):
        data = {
            "email": validated_data.get("email"),
            "password": make_password(validated_data.get("password")),
            "is_active": True,
        }
        user: User = User.objects.create(**data)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "email",
            "is_active",
        ]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"


class SendMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"

        extra_kwargs = {
            "sender": {"read_only": True},
            "is_read": {"read_only": True},
        }
    
    def validate(self, attrs:dict):
        auth_user : User = self.context["request"].user
        if  auth_user == attrs.get("receiver"):
            raise serializers.ValidationError(
                {'receiver': 'You cannot message yourself'})
        return super().validate(attrs)
    
    def create(self, validated_data: dict):
        auth_user : User = self.context["request"].user
        msg: Message = Message.objects.create(**validated_data, sender=auth_user)
        return msg