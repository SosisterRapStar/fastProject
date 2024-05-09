from os import name
from timeit import repeat
from faker import Faker
import uuid
from src.schemas.users import (
    User_for_update,
    User_on_request,
    User_on_response,
    CreateUser,
)
from src.schemas.conversation import (
    ConversationRequest,
    ConversationBase,
    ConversationRequestBase,
    ConversationResponse,
    ConversationUpdate,
    AddUser,
)

def get_random_word():
    return Faker().word()

class BaseFactory:
    @classmethod
    def generate_id(cls):
        return str(uuid.uuid4())


class ConversationFactory(BaseFactory):
    @classmethod
    def generate_name(cls):
        return Faker().word()


class ConversationUpdateFactory(ConversationFactory):
    @classmethod
    def build(cls):
        name = cls.generate_name()
        return ConversationUpdate(name=name)


class AddUserFactory(BaseFactory):
    @classmethod
    def build(cls, is_moder: bool = False):
        id = cls.generate_id()
        return AddUser(user_id=id, is_moder=is_moder)


class ConversationRequestFactory(ConversationFactory):
    @classmethod
    def build(cls):
        name = cls.generate_name()
        return ConversationRequest(name=name)

class ConversationResponseFactory(ConversationFactory):
    @classmethod
    def build(cls):
        id = cls.generate_id()
        name = cls.generate_name()
        user_admin_fk = cls.generate_id()
        return ConversationResponse(id=id, name=name, user_admin_fk=user_admin_fk)

class UserFactory(BaseFactory):
    @classmethod
    def generate_name(cls):
        return Faker().name()[:20]

    @classmethod
    def generate_password(cls):
        return Faker().password(
            length=12, special_chars=True, digits=True, upper_case=True, lower_case=True
        )

    @classmethod
    def generate_email(cls):
        return Faker().email()


class CreateUserFactory(UserFactory):
    @classmethod
    def build(cls):
        name = cls.generate_name()
        email = cls.generate_email()
        password = cls.generate_password()
        password_repeat = password
        return CreateUser(
            name=name, email=email, password=password, password_repeat=password_repeat
        )


class UserforUpdateFactory(UserFactory):
    @classmethod
    def build(cls):
        name = cls.generate_name()
        email = cls.generate_email()
        password = cls.generate_password()
        return User_for_update(name=name, email=email, password=password)


class UserOnResponseFactory(UserFactory):
    @classmethod
    def build(cls):
        id = cls.generate_id()
        name = cls.generate_name()
        email = cls.generate_email()
        password = cls.generate_password()
        password_repeat = password
        return User_on_response(
            id=id,
            name=name,
            email=email,
            password=password,
            password_repeat=password_repeat,
        )


class UserOnRequestFactory(UserFactory):
    @classmethod
    def build(cls):
        name = cls.generate_name()
        email = cls.generate_email()
        password = cls.generate_password()
        return User_on_request(name=name, email=email, password=password)
