import uuid
from typing import Annotated

from fastapi import Path, HTTPException, Depends


from src.crud import user_crud
from src.dependencies.session_dependency import session_dep

from src.models.user_model import User


async def user_by_id(user_id: Annotated[uuid.UUID, Path(title="The ID of the item to get")],
                        session: session_dep) -> User:
    user = await user_crud.get_user_by_id(async_session=session, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


get_by_id_dep = Annotated[User, Depends(user_by_id)]
