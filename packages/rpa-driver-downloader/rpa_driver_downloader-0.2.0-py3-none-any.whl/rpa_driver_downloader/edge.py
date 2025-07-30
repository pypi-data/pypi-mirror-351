from .base import BaseDriver
import platform
import requests


class Edge(BaseDriver):
    def __init__(self, version: str = None):
        self.version = version or "124.0.2478.0"  # Default fallback version
        super().__init__(version=self.version)


    @property
    def key_name(self) -> str:
        return "edgedriver_path"


    def get_latest_version(self) -> str:
        return self.version


    def get_download_url(self) -> str:
        os_name = platform.system()
        url = f"https://msedgedriver.azureedge.net/{self.version}/edgedriver_"

        if os_name == "Windows":
            url += "win64.zip"
        elif os_name == "Linux":
            url += "linux64.zip"
        elif os_name == "Darwin":
            url += "mac64.zip"
        else:
            raise FileNotFoundError("Edge driver download URL not found.")

        resp = requests.get(url, stream=True)
        if resp.status_code != 200:
            raise ValueError(
                f"❌ EdgeDriver version '{self.version}' not found.\n"
                f"🔗 See all versions at: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/"
            )
        return url