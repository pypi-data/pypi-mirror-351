import os
import json
import requests
import zipfile
import tarfile

from pathlib import Path
from abc import ABC, abstractmethod


SETTINGS_PATH = Path("settings.json")
DRIVER_DIR = Path("drivers")


class BaseDriver(ABC):
    """
    Abstract base class for downloading and managing browser drivers.
    """
    def __init__(self, version: str = None):
        self.version = version
        self.settings = self._load_or_create_settings()


    @property
    @abstractmethod
    def key_name(self) -> str:
        """
        Unique identifier used in settings.json to track driver path and version.
        """
        ...


    @abstractmethod
    def get_download_url(self) -> str:
        """
        Returns the download URL for the desired version (self.version) or latest version.
        """
        ...


    @abstractmethod
    def get_latest_version(self) -> str:
        """
        Returns the latest version number of the driver as a string.
        """
        ...


    def path_for_the_driver(self) -> str:
        """
        Returns the absolute path of the browser driver. If the driver does not exist
        or is outdated, downloads and replaces it with the latest version or specified version.
        """
        driver_path = self.settings.get(self.key_name)
        current_version = self.settings.get(f"{self.key_name}_version")
        target_version = self.version or self.get_latest_version()

        if driver_path and Path(driver_path).exists() and current_version == target_version:
            return driver_path

        print(f"🔍 Updating or downloading driver '{self.key_name}' to version: {target_version}")
        url = self.get_download_url()
        driver_path = self.download_and_extract(url)

        self.settings[self.key_name] = driver_path
        self.settings[f"{self.key_name}_version"] = target_version
        self._save_settings()
        return driver_path


    @classmethod
    def get_driver_path(cls, version: str = None) -> str:
        """
        Class method to quickly get the driver path without explicitly creating an instance.
        Instantiates the driver internally and calls `path_for_the_driver`.

        Parameters:
            version (str): Optional specific version to download.

        Returns:
            str: The absolute path to the browser driver executable.
        """
        instance = cls(version=version)
        return instance.path_for_the_driver()


    def _load_or_create_settings(self) -> dict:
        """
        Loads the settings from settings.json or creates a new one if not found.
        """
        if SETTINGS_PATH.exists():
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}


    def _save_settings(self) -> None:
        """
        Saves the current settings to settings.json.
        """
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=4)


    def download_and_extract(self, url: str) -> str:
        DRIVER_DIR.mkdir(exist_ok=True)
        file_name = url.split("/")[-1]
        archive_path = DRIVER_DIR / file_name

        # Download
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(archive_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        # Extract
        if file_name.endswith(".zip"):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(DRIVER_DIR)
        elif file_name.endswith(".tar.gz"):
            with tarfile.open(archive_path, 'r:gz') as tar_ref:
                tar_ref.extractall(DRIVER_DIR)

        archive_path.unlink()

        expected_names = {
            "geckodriver_path": ["geckodriver.exe", "geckodriver"],
            "chromiumdriver_path": ["chromedriver.exe", "chromedriver"],
            "edgedriver_path": ["msedgedriver.exe", "msedgedriver"]
        }

        candidates = expected_names.get(self.key_name, [])

        for root, dirs, files in os.walk(DRIVER_DIR):
            for file in files:
                if file in candidates:
                    driver_path = Path(root) / file
                    driver_path.chmod(0o755)
                    return str(driver_path.resolve())

        raise FileNotFoundError(
            f"Driver was extracted but no executable file found for key '{self.key_name}'. "
            f"Expected one of: {candidates} in {DRIVER_DIR.resolve()}"
        )