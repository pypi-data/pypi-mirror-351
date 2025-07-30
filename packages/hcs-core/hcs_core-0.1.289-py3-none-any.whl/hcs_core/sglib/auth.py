"""
Copyright 2023-2023 VMware Inc.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import hashlib
import json
import logging
import threading
import time

import jwt
from authlib.integrations.httpx_client import OAuth2Client

from hcs_core.ctxp import CtxpException, panic, profile
from hcs_core.ctxp.jsondot import dotdict, dotify

from .csp import CspClient

log = logging.getLogger(__name__)


def _get_profile_auth_hash(effective_profile):
    csp = effective_profile.csp
    text = json.dumps(csp, default=vars)
    return profile.name() + "#" + hashlib.md5(text.encode("ascii"), usedforsecurity=False).hexdigest()


def _is_auth_valid(auth_data, effective_profile):
    if not auth_data:
        return
    if not auth_data.token:
        return
    if auth_data.hash != _get_profile_auth_hash(effective_profile):
        return
    leeway = 60
    if time.time() + leeway >= auth_data.token.expires_at:
        return
    return True


def _decode_http_basic_auth_token(basic_token: str):
    import base64

    try:
        decoded = base64.b64decode(basic_token).decode("utf-8")
        client_id, client_secret = decoded.split(":")
        return client_id, client_secret
    except Exception as e:
        raise CtxpException(f"Invalid basic http auth token: {e}")


_login_lock = threading.Lock()


def login(force_refresh: bool = False, panic_on_failure: bool = True):
    """Ensure login state, using credentials from the current profile. Return oauth token."""

    _login_lock.acquire()
    try:
        effective_profile = profile.current()

        auth_data = profile.auth.get()
        if force_refresh or not _is_auth_valid(auth_data, effective_profile):
            oauth_token = _get_new_oauth_token(auth_data.token, effective_profile)
            if oauth_token:
                use_oauth_token(oauth_token, effective_profile)
            elif panic_on_failure:
                panic(
                    "Login failed. If this is configured API key or client credential, refresh the credential from CSP and update profile config. If this is browser based interactive login, login again."
                )
            else:
                return None
        else:
            oauth_token = auth_data.token
        return oauth_token
    finally:
        _login_lock.release()


def _get_new_oauth_token(old_oauth_token, effective_profile):
    csp_config = effective_profile.csp

    csp_client = CspClient(url=csp_config.url)

    if csp_config.apiToken:
        oauth_token = csp_client.login_with_api_token(csp_config.apiToken)
    elif csp_config.clientId:
        oauth_token = csp_client.login_with_client_id_and_secret(
            csp_config.clientId, csp_config.clientSecret, csp_config.orgId
        )
    elif csp_config.basic:
        client_id, client_secret = _decode_http_basic_auth_token(csp_config.basic)
        oauth_token = csp_client.login_with_client_id_and_secret(client_id, client_secret, csp_config.orgId)
    else:
        # This should be a config from interactive login.
        # Use existing oauth_token to refresh.
        if not old_oauth_token:
            old_oauth_token = profile.auth.get().token
        if old_oauth_token:
            try:
                oauth_token = refresh_oauth_token(old_oauth_token, csp_config.url)
            except Exception as e:
                oauth_token = None
                log.warning(e)
        else:
            oauth_token = None

    if oauth_token and not oauth_token.get("expires_at"):
        oauth_token["expires_at"] = int(time.time() + oauth_token["expires_in"])

    return oauth_token


def refresh_oauth_token(old_oauth_token: dict, csp_url: str):
    with OAuth2Client(token=old_oauth_token) as client:
        log.debug("Refresh auth token...")
        token_url = csp_url + "/csp/gateway/am/api/auth/token"
        from .login_support import identify_client_id

        csp_specific_req_not_oauth_standard = (identify_client_id(csp_url), "")
        new_token = client.refresh_token(token_url, auth=csp_specific_req_not_oauth_standard)
        log.debug(f"New auth token: {new_token}")
        if not new_token:
            raise Exception("CSP auth refresh failed.")
        if "cspErrorCode" in new_token:
            raise Exception(f"CSP auth failed: {new_token.get('message')}")

    return new_token


class MyOAuth2Client(OAuth2Client):
    def __init__(self):
        super().__init__()

    def ensure_token(self):
        # pylint: disable=access-member-before-definition
        if self.token is None or not super().ensure_active_token():
            self.token = login()


def oauth_client():
    return MyOAuth2Client()


def details(get_org_details: bool = False) -> dotdict:
    """Get the auth details, for the current profile"""
    oauth_token = login()
    if not oauth_token:
        return
    return details_from_token(oauth_token, get_org_details)


def details_from_token(oauth_token, get_org_details: bool = False):
    decoded = jwt.decode(oauth_token["access_token"], options={"verify_signature": False})
    org_id = decoded["context_name"]
    ret = {"token": oauth_token, "jwt": decoded, "org": {"id": org_id}}

    if get_org_details:
        csp_client = CspClient(url=profile.current().csp.url, oauth_token=oauth_token)
        try:
            org_details = csp_client.get_org_details(org_id)
        except Exception as e:
            org_details = {"error": f"Fail retrieving org details: {e}"}
        ret["org"].update(org_details)
    return dotify(ret)


def get_org_id_from_token(oauth_token: str) -> str:
    decoded = jwt.decode(oauth_token["access_token"], options={"verify_signature": False})
    return decoded["context_name"]


def use_oauth_token(oauth_token, effective_profile=None):
    if effective_profile is None:
        effective_profile = profile.current()
    profile.auth.set({"token": oauth_token, "hash": _get_profile_auth_hash(effective_profile)})
