"""AuthService class to handle auth service."""

import logging
from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase

from zmp_authentication_provider.db.basic_auth_user_repository import (
    BasicAuthUserRepository,
)
from zmp_authentication_provider.exceptions import (
    AuthBackendException,
    AuthError,
    InvalidObjectIDException,
    ObjectNotFoundException,
)
from zmp_authentication_provider.scheme.auth_model import BasicAuthUser
from zmp_authentication_provider.setting import auth_default_settings

log = logging.getLogger(__name__)


class AuthService:
    """AuthService class to handle auth service."""

    def __init__(self, *, database: AsyncIOMotorDatabase):
        """Initialize the repository with MongoDB database."""
        self._database = database
        self._basic_auth_user_repository = BasicAuthUserRepository(
            collection=self._database[auth_default_settings.basic_auth_user_collection]
        )

        log.info(f"{__name__} AuthService Initialized")

    async def create_basic_auth_user(self, user: BasicAuthUser) -> str:
        """Create a basic auth user."""
        try:
            return await self._basic_auth_user_repository.insert(user)
        except ValueError as e:
            raise AuthBackendException(AuthError.BAD_REQUEST, details=str(e))

    async def modify_basic_auth_user(self, user: BasicAuthUser) -> BasicAuthUser:
        """Update a basic auth user."""
        try:
            return await self._basic_auth_user_repository.update(user)
        except ObjectNotFoundException:
            raise AuthBackendException(
                AuthError.ID_NOT_FOUND,
                document=auth_default_settings.basic_auth_user_collection,
                object_id=user.id,
            )
        except InvalidObjectIDException as e:
            raise AuthBackendException(AuthError.INVALID_OBJECTID, details=str(e))

    async def remove_basic_auth_user(self, id: str) -> bool:
        """Delete a basic auth user by id."""
        if not id:
            raise AuthBackendException(AuthError.BAD_REQUEST, details="ID is required")

        try:
            return await self._basic_auth_user_repository.delete_by_id(id)
        except ObjectNotFoundException:
            raise AuthBackendException(
                AuthError.ID_NOT_FOUND,
                document=auth_default_settings.basic_auth_user_collection,
                object_id=id,
            )
        except InvalidObjectIDException as e:
            raise AuthBackendException(AuthError.INVALID_OBJECTID, details=str(e))

    async def get_basic_auth_user_by_username(self, username: str) -> BasicAuthUser:
        """Get a basic auth user by username."""
        if not username:
            raise AuthBackendException(
                AuthError.BAD_REQUEST, details="Username is required"
            )

        try:
            return await self._basic_auth_user_repository.find_by_username(username)
        except ObjectNotFoundException:
            raise AuthBackendException(
                AuthError.ID_NOT_FOUND,
                document=auth_default_settings.basic_auth_user_collection,
                object_id=username,
            )
        except InvalidObjectIDException as e:
            raise AuthBackendException(AuthError.INVALID_OBJECTID, details=str(e))

    async def get_basic_auth_users(self) -> List[BasicAuthUser]:
        """Get basic auth users."""
        return await self._basic_auth_user_repository.find()
