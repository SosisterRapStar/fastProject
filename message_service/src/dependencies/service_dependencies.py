
from typing import Annotated

from fastapi import Depends
from .repo_providers_dependency import user_repo_provider, invite_repo_provider
from src.services.friends_service import FriendsService

def get_friends_service(user_repo: user_repo_provider,
                        invite_repo: invite_repo_provider,):
    return FriendsService(user_repo=user_repo, 
                          invite_repo=invite_repo,)


friends_service_provider = Annotated[FriendsService, Depends(get_friends_service)]