"""This module contains the routes for the basic auth user."""

import logging
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from zmp_authentication_provider.auth.oauth2_keycloak import TokenData, get_current_user
from zmp_authentication_provider.scheme.auth_model import BasicAuthUser
from zmp_authentication_provider.scheme.basicauth_request_model import (
    BasicAuthUserCreateRequest,
    BasicAuthUserUpdateRequest,
)
from zmp_authentication_provider.service.auth_service import AuthService
from zmp_authentication_provider.setting import auth_default_settings

log = logging.getLogger(__name__)

router = APIRouter()


async def get_auth_service(request: Request) -> AuthService:
    """Get the auth service."""
    service = getattr(request.app.state, auth_default_settings.service_name, None)
    if not service:
        raise HTTPException(
            status_code=500,
            detail=f"Service '{auth_default_settings.service_name}' not available in the request state. "
            "You should set the service in the request state.",
        )

    return service


@router.get(
    "/basic_auth_users",
    summary="Get basic auth users",
    response_class=JSONResponse,
    response_model=List[BasicAuthUser],
    response_model_by_alias=False,
    response_model_exclude_none=False,
)
async def get_basic_auth_users(
    oauth_user: TokenData = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> List[BasicAuthUser]:
    """Get all basic auth users."""
    return auth_service.get_basic_auth_users()


@router.post(
    "/basic_auth_users",
    summary="Create a basic auth user",
    response_class=JSONResponse,
    response_model=Dict[str, str],
    response_model_by_alias=False,
    response_model_exclude_none=True,
)
async def create_basic_auth_user(
    basic_auth_user_create_request: BasicAuthUserCreateRequest,
    oauth_user: TokenData = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> Dict[str, str]:
    """Create a basic auth user."""
    basic_auth_user = BasicAuthUser(**basic_auth_user_create_request.model_dump())
    basic_auth_user.modifier = oauth_user.username
    return {"inserted_id": auth_service.create_basic_auth_user(basic_auth_user)}


@router.get(
    "/basic_auth_users/{username}",
    summary="Get a basic auth user by username",
    response_class=JSONResponse,
    response_model=BasicAuthUser,
    response_model_by_alias=False,
    response_model_exclude_none=False,
)
async def get_basic_auth_user_by_username(
    username: str,
    oauth_user: TokenData = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> BasicAuthUser:
    """Get a basic auth user by username."""
    return auth_service.get_basic_auth_user_by_username(username)


@router.delete(
    "/basic_auth_users/{id}",
    summary="Remove a basic auth user",
    response_class=JSONResponse,
    response_model=Dict[str, str],
    response_model_by_alias=False,
    response_model_exclude_none=True,
)
async def remove_basic_auth_user(
    id: str,
    oauth_user: TokenData = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> Dict[str, str]:
    """Remove a basic auth user."""
    auth_service.remove_basic_auth_user(id)
    return {"result": "success"}


@router.put(
    "/basic_auth_users",
    summary="Modify a basic_auth_user",
    response_class=JSONResponse,
    response_model=BasicAuthUser,
    response_model_by_alias=False,
    response_model_exclude_none=True,
)
async def modify_basic_auth_user(
    basic_auth_user_update_request: BasicAuthUserUpdateRequest,
    oauth_user: TokenData = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> BasicAuthUser:
    """Modify a basic auth user."""
    basic_auth_user = BasicAuthUser(**basic_auth_user_update_request.model_dump())
    basic_auth_user.modifier = oauth_user.username
    return auth_service.modify_basic_auth_user(basic_auth_user)
