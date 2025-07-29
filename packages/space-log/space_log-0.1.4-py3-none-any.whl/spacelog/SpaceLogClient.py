import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import requests
from dateutil import parser

from spacelog.SpaceLogHeartbeat import SpaceLogHeartbeat


@dataclass
class SpaceLogPingInfo:
    id: str
    group: str
    application: str
    is_observed: bool
    last_ping: datetime
    project: str


class SpaceLogClient:
    DEFAULT_SUPABASE_PROJECT_ID = "qtdiupshceorsdarittk"

    SPACE_LOG_PROJECT_ID_ENV_NAME = "SPACE_LOG_PROJECT_ID"
    SPACE_LOG_APP_ID_ENV_NAME = "SPACE_LOG_APP_ID"
    SPACE_LOG_AUTH_TOKEN_ENV_NAME = "SPACE_LOG_TOKEN"

    def __init__(self, application_id: str,
                 auth_token: Optional[str] = None,
                 supabase_project: Optional[str] = None):
        self.application_id = application_id
        self.auth_token = os.environ.get(self.SPACE_LOG_AUTH_TOKEN_ENV_NAME) if auth_token is None else auth_token
        self.supabase_project = os.environ.get(self.SPACE_LOG_PROJECT_ID_ENV_NAME,
                                               self.DEFAULT_SUPABASE_PROJECT_ID) if supabase_project is None else supabase_project

        if self.auth_token is None:
            logging.error(f"SpaceLog: auth token is not set! "
                          f"Please set environment variable '{self.SPACE_LOG_AUTH_TOKEN_ENV_NAME}'")

    @property
    def base_url(self) -> str:
        return f"https://{self.supabase_project}.supabase.co"

    def send_ping(self) -> Optional[SpaceLogPingInfo]:
        url = f"{self.base_url}/functions/v1/send-ping?guid={self.application_id}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.auth_token}"
        }

        try:
            response = requests.get(url, headers=headers)
        except Exception as ex:
            logging.warning(f"SpaceLog: Could not send ping ({ex})")
            return None

        if response.status_code != 200:
            logging.error(f"SpaceLog: Error while pinging ({response.text})")
            return None

        response_data = response.json()

        if "data" in response_data:
            data = response_data["data"]

            if len(data) > 0:
                entry = data[0]
                last_ping = parser.parse(entry["last_ping"])

                # Creating an instance of PingInfo with the first entry data
                ping_info = SpaceLogPingInfo(
                    id=entry["id"],
                    group=entry["group"],
                    application=entry["application"],
                    is_observed=entry["is_observed"],
                    last_ping=last_ping,
                    project=entry["project"]
                )

                return ping_info

        return None

    def start_heartbeat(self, interval: float = 60) -> SpaceLogHeartbeat:
        heartbeat = SpaceLogHeartbeat(self, interval)
        heartbeat.start()
        return heartbeat

    @staticmethod
    def from_environment(application_id: Optional[str] = None,
                         auth_token: Optional[str] = None,
                         supabase_project: Optional[str] = None) -> Optional["SpaceLogClient"]:

        app_id = os.environ.get(SpaceLogClient.SPACE_LOG_APP_ID_ENV_NAME) if application_id is None else application_id
        token = os.environ.get(SpaceLogClient.SPACE_LOG_AUTH_TOKEN_ENV_NAME) if auth_token is None else auth_token
        supabase_project = os.environ.get(SpaceLogClient.SPACE_LOG_PROJECT_ID_ENV_NAME,
                                          SpaceLogClient.DEFAULT_SUPABASE_PROJECT_ID) if supabase_project is None else supabase_project

        if app_id is None:
            logging.warning(f"Spacelog could not find env var {SpaceLogClient.SPACE_LOG_APP_ID_ENV_NAME}")
            return None

        if token is None:
            logging.warning(f"Spacelog could not find env var {SpaceLogClient.SPACE_LOG_AUTH_TOKEN_ENV_NAME}")
            return None

        return SpaceLogClient(app_id, token, supabase_project)
