import platform
import requests
from logger import logger
import json

def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load JSON from {file} (Error: {e})")
        return None


class UpdateChecker:
    def __init__(self):
        self.data_url = "https://gist.githubusercontent.com/chestnutcapybara/193b05cf99947c5f62e199b74a490a7e/raw/d5e43c6a259377acedcbbc67375de767a1d1b94c/version.json"
        self.platform = platform.system().lower()

        self.data = None
        self.online_version = None

        self._load_remote_data()

    def _load_remote_data(self):
        try:
            r = requests.get(self.data_url, timeout=5)
            r.raise_for_status()
            self.data = r.json()
            self.online_version = self.data["capyutilities"]["version"]
            logger.info(f"Online version found: {self.online_version}")

        except Exception as e:
            logger.error(f"Failed to fetch online version: {e}")
            self.data = None
            self.online_version = None

    def check_for_updates(self):
        local_version_data = load_json("version.json")

        if not local_version_data:
            logger.warning("No local version found. Assuming update required.")
            return True  # or force update flow

        local_version = local_version_data.get("version")

        if not self.online_version:
            logger.warning("Cannot check updates (offline mode).")
            return False

        if local_version != self.online_version:
            logger.info(f"Update available! {local_version} → {self.online_version}")
            return True

        logger.info("CapyUtilities is up to date.")
        return False