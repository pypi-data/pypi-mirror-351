from .base import BaseDriver
import platform
import requests


class Gecko(BaseDriver):
    def __init__(self, version: str = None):
        self.version = version
        super().__init__(version=version)


    @property
    def key_name(self) -> str:
        return "geckodriver_path"


    def get_latest_version(self) -> str:
        url = "https://api.github.com/repos/mozilla/geckodriver/releases/latest"
        data = requests.get(url).json()
        return data["tag_name"].lstrip("v")


    def get_download_url(self) -> str:
        os_name = platform.system()

        if self.version:
            url = f"https://api.github.com/repos/mozilla/geckodriver/releases/tags/v{self.version}"
        else:
            url = "https://api.github.com/repos/mozilla/geckodriver/releases/latest"

        resp = requests.get(url)
        if resp.status_code != 200:
            raise ValueError(
                f"❌ GeckoDriver version '{self.version}' not found.\n"
                f"🔗 See all versions at: https://github.com/mozilla/geckodriver/releases"
            )

        data = resp.json()
        for asset in data["assets"]:
            name = asset["name"]
            if os_name == "Windows" and "win64.zip" in name:
                return asset["browser_download_url"]
            elif os_name == "Linux" and "linux64.tar.gz" in name:
                return asset["browser_download_url"]
            elif os_name == "Darwin" and "macos" in name:
                return asset["browser_download_url"]

        raise FileNotFoundError("Driver asset not found for your OS.")