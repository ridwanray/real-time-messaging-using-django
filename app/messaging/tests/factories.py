import factory
from faker import Faker
from messaging.models import User, Message

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: "person{}@example.com".format(n))
    password = factory.PostGenerationMethodCall("set_password", "passer@@@111")
    is_active = True


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message

    content = fake.text()