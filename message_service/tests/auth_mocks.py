from src.authorization.exceptions import UserCredentialsError


async def mock_get_token(self):
    data = self.data
    repo = self.repo
    user = await repo.get(name=data.username)
    if data.password != user.password:
        raise UserCredentialsError()
    name: str = "_" + self.__class__.__name__ + "__get_user_token"
    return await getattr(self, name)(user=user)
