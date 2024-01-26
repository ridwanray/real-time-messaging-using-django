import pytest
from django.urls import reverse

from .conftest import api_client_with_credentials
from .factories import MessageFactory

pytestmark = pytest.mark.django_db


class TestMessages:
    def test_create_message(self, api_client, authenticate_user, user_factory):
        user = authenticate_user()
        token = user["token"]
        receiver = user_factory()

        data = {
            "receiver": str(receiver.id),
            "content": "Hi, how are you?",
        }

        api_client_with_credentials(token, api_client)
        create_message_url = reverse("message:message-list")
        response = api_client.post(create_message_url, data)

        assert response.status_code == 201
        returned_json = response.json()
        assert "id" in returned_json
        assert returned_json["sender"] == str(user["user_instance"].id)
        assert returned_json["receiver"] == str(receiver.id)
        assert returned_json["content"] == data["content"]

    def test_deny_messaging_yourself(self, api_client, authenticate_user):
        user = authenticate_user()
        token = user["token"]

        data = {
            "receiver": str(user["user_instance"].id),
            "content": "Hi, how are you?",
        }

        api_client_with_credentials(token, api_client)
        create_message_url = reverse("message:message-list")
        response = api_client.post(create_message_url, data)
        assert response.status_code == 400

    def test_update_message(self, api_client, authenticate_user, user_factory):
        user = authenticate_user()
        token = user["token"]

        msg_object = MessageFactory(
            sender=user_factory(), receiver=user["user_instance"], is_read=False
        )

        api_client_with_credentials(token, api_client)
        read_message_url = reverse(
            "message:message-read-message", kwargs={"pk": str(msg_object.id)}
        )
        response = api_client.post(read_message_url)

        assert response.status_code == 200
        msg_object.refresh_from_db()
        assert msg_object.is_read == True

    def test_deny_reading_unowned_message(
        self, api_client, authenticate_user, user_factory
    ):
        """Deny setting status of message when user is not the receiver"""
        user = authenticate_user()
        token = user["token"]

        msg_object = MessageFactory(
            sender=user_factory(), receiver=user_factory(), is_read=False
        )

        api_client_with_credentials(token, api_client)
        read_message_url = reverse(
            "message:message-read-message", kwargs={"pk": str(msg_object.id)}
        )
        response = api_client.post(read_message_url)

        assert response.status_code == 400
