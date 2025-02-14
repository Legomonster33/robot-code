"""Serves as an abstraction layer for connecting with the Onshape API and the current flask request."""

import enum
from typing import Any

from uuid import uuid4
import flask
from requests_oauthlib import OAuth2Session

from backend.common.database import Database
import onshape_api
from backend.common import backend_exceptions, env
from onshape_api.paths.instance_type import InstanceType


def get_session_id() -> str:
    session_id = flask.session.get("session_id")
    if session_id is None:
        session_id = str(uuid4())
        flask.session["session_id"] = session_id
    return session_id


def get_token(db: Database) -> dict | None:
    return get_session_data(db).get("token")


def save_token(db: Database, token) -> None:
    set_session_data(db, {"token": token})


def get_session_data(db: Database) -> dict:
    session_id = get_session_id()
    doc_ref = db.sessions.document(document_id=session_id)
    doc = doc_ref.get()
    if not doc.exists or (session_data := doc.to_dict()) is None:
        session_data = {"token": None}
    return session_data


def set_session_data(db: Database, session_data: dict) -> None:
    session_id = get_session_id()
    doc_ref = db.sessions.document(document_id=session_id)
    doc_ref.set(session_data)


base_url = "https://oauth.onshape.com/oauth"
auth_base_url = base_url + "/authorize"
token_url = base_url + "/token"


class OAuthType(enum.Enum):
    SIGN_IN = enum.auto()
    REDIRECT = enum.auto()
    USE = enum.auto()


def get_oauth_session(
    db: Database, oauth_type: OAuthType = OAuthType.USE
) -> OAuth2Session:
    if oauth_type == OAuthType.SIGN_IN:
        return OAuth2Session(env.client_id)
    elif oauth_type == OAuthType.REDIRECT:
        return OAuth2Session(env.client_id, state=flask.request.args["state"])

    refresh_kwargs = {
        "client_id": env.client_id,
        "client_secret": env.client_secret,
    }

    def _save_token(token) -> None:
        save_token(db, token)

    return OAuth2Session(
        env.client_id,
        token=get_token(db),
        auto_refresh_url=token_url,
        auto_refresh_kwargs=refresh_kwargs,
        token_updater=_save_token,
    )


def instance_route(wvm_param: str = "w"):
    return f"/d/<document_id>/<{wvm_param}>/<workspace_id>"


def element_route(wvm_param: str = "w"):
    return instance_route(wvm_param) + "/e/<element_id>"


def get_api(db: Database) -> onshape_api.OAuthApi:
    return onshape_api.make_oauth_api(get_oauth_session(db))


def get_route_instance_path(wvm_param: str = "w") -> onshape_api.InstancePath:
    return onshape_api.InstancePath(
        get_route("document_id"),
        get_route("workspace_id"),
        get_route(wvm_param),
    )


def get_route_element_path(wvm_param: str = "w") -> onshape_api.ElementPath:
    return onshape_api.ElementPath.from_path(
        get_route_instance_path(wvm_param),
        get_route("element_id"),
    )


def get_body_instance_path(
    *instance_types: InstanceType, default_type: InstanceType = InstanceType.WORKSPACE
) -> onshape_api.InstancePath:
    instance_type = get_body_optional("instanceType")
    if instance_type == None:
        instance_type = default_type
    # Only do validation if instance type passed
    elif instance_type not in instance_types:
        raise backend_exceptions.BackendException(
            "Invalid instance type {}.".format(instance_type)
        )

    return onshape_api.InstancePath(
        get_body("documentId"), get_body("instanceId"), instance_type
    )


def get_body_element_path() -> onshape_api.ElementPath:
    return onshape_api.ElementPath.from_path(
        get_body_instance_path(),
        get_route("elementId"),
    )


def get_route(route_param: str) -> str:
    """Returns the value of a path parameter.

    Throws if it doesn't exist.
    """
    view_args = flask.request.view_args
    if view_args is None or (param := view_args.get(route_param)) is None:
        raise backend_exceptions.ClientException(
            "Missing required path parameter {}.".format(route_param)
        )
    return param


def get_query(key: str) -> str:
    """Returns a value from the request query.

    Throws if it doesn't exist.
    """
    value = flask.request.args.get(key)
    if value is None:
        raise backend_exceptions.ClientException(
            "Missing required query parameter {}.".format(key)
        )
    return value


def get_body(key: str) -> Any:
    """Returns a value from the request body.

    Throws if key doesn't exist.
    """
    value = flask.request.get_json().get(key, None)
    if not value:
        raise backend_exceptions.ClientException(
            "Missing required body parameter {}.".format(key)
        )
    return value


def get_body_optional(key: str, default: Any | None = None) -> Any:
    """Returns a value from the request body, or default if it doesn't exist."""
    return flask.request.get_json().get(key, default)


# def extract_body(
#     required_keys: Iterable[str] = [],
#     optional_keys: Iterable[str] = [],
# ) -> dict:
#     required_key_set = set(required_keys)
#     optional_key_set = set(optional_keys)

#     body = request.get_json()
#     for key in body:
#         if key in required_key_set:
#             required_key_set.remove(key)
#             continue
#         elif key in optional_key_set:
#             continue
#         message = "Required arguments are missing: {}".format(
#             ", ".join(required_key_set)
#         )
#         raise exceptions.ApiException(message)
#     return body
