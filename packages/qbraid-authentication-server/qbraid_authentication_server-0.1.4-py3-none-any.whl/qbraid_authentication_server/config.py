import json
import sys
from typing import Optional

import tornado
from jupyter_server.base.handlers import APIHandler
from qbraid_core import QbraidSession


class UserConfigHandler(APIHandler):
    """Handler for managing user configurations and other local data."""

    @tornado.web.authenticated
    def get(self):
        """Get user's qBraid credentials."""
        config = self.get_config()

        self.finish(json.dumps(config))

    @tornado.web.authenticated
    def post(self):
        """Update user's qBraid credentials."""
        try:
            data: dict = json.loads(self.request.body.decode("utf-8"))
            session = QbraidSession()
            session.save_config(
                user_email=data.get("email"), refresh_token=data.get("refreshToken")
            )
            config = self.get_config()
            self.finish(json.dumps({"status": "success", "config": config}))
        except Exception as e:
            print(f"Error while updating user configuration: {str(e)}", file=sys.stderr)
            self.finish(json.dumps({"status": "error", "message": str(e)}))

    @staticmethod
    def get_config() -> dict[str, Optional[str]]:
        """
        Retrieve the user's qBraid credentials.

        Returns:
            A dictionary containing user configuration details.
        """
        try:
            session = QbraidSession()
            # TODO: Load config once. Currently reads file every time get_config is called.
            config = {
                "email": session.get_config("email"),
                "refreshToken": session.get_config("refresh-token"),
                "apiKey": session.get_config("api-key"),
                "organization": session.get_config("organization"),
                "workspace": session.get_config("workspace"),
                "url": session.get_config("url"),
            }
            return config
        except Exception as e:
            print(f"Error while retrieving user configuration: {str(e)}", file=sys.stderr)
            return {
                key: None
                for key in ["email", "refreshToken", "apiKey", "url", "organization", "workspace"]
            }
