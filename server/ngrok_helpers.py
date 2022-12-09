import subprocess
import requests

class NgrokTunnel():
    def __init__(self, port: int = 80, web_addr: str = "localhost:4040"):
        self.port = port
        self.web_addr = web_addr
        self.tunnel = None

    def __open(self):
        self.tunnel = subprocess.Popen(["ngrok", "http", str(self.port)], stdout=subprocess.DEVNULL)

    def __close(self):
        self.tunnel.kill()

    def _get_url(self) -> str:
        response = requests.get(f"http://{self.web_addr}/api/tunnels")
        return response.json()["tunnels"][0]["public_url"]

    def __enter__(self):
        self.__open()
        return self._get_url()

    def __exit__(self, exc_type, exc_value, traceback):
        self.__close()

    def __del__(self):
        self.__close()
