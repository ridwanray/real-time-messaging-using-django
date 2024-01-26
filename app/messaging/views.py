from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Message, User
from .serializers import (
    CustomObtainTokenPairSerializer,
    MessageSerializer,
    OnboardUserSerializer,
    PasswordChangeSerializer,
    SendMessageSerializer,
    UserSerializer,
)


class CustomObtainTokenPairView(TokenObtainPairView):
    """Authentice with email and password"""

    serializer_class = CustomObtainTokenPairSerializer


class PasswordChangeView(viewsets.GenericViewSet):
    """Enables authenticated users to change their passwords."""

    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        context = {"request": request}
        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Your password has been updated."}, status.HTTP_200_OK
        )


class UserViewsets(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = [
        "get",
        "post",
    ]

    def get_queryset(self):
        user: User = self.request.user
        return super().get_queryset().filter(id=user.id)

    def get_serializer_class(self):
        if self.action == "create":
            return OnboardUserSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        permission_classes = self.permission_classes
        if self.action in ["create"]:
            permission_classes = [AllowAny]
        elif self.action in ["list"]:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @extend_schema(responses={200: UserSerializer()})
    def create(self, request, *args, **kwargs):
        """Accounts are automatically activated upon creation."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"success": True, "message": "Account Created! Login now."}, status=status.HTTP_200_OK
        )


class MessageViewsets(viewsets.ModelViewSet):
    queryset = Message.objects.select_related("sender", "receiver").all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = [
        "post",
    ]

    def get_serializer_class(self):
        if self.action == "create":
            return SendMessageSerializer
        return super().get_serializer_class()

    @action(
        methods=["POST"], detail=True, serializer_class=None, url_path="read-message"
    )
    def read_message(self, request, *args, **kwargs):
        """Update a message read status"""
        message_obj: Message = self.get_object()
        if message_obj.receiver != self.request.user:
            return Response(
                {"success": False, "errors": "This message is not sent to you!"},
                status.HTTP_400_BAD_REQUEST,
            )
        message_obj.is_read = True
        message_obj.save(update_fields=["is_read"])
        return Response({"success": True, "message": "Marked as read!"}, status=status.HTTP_200_OK)
