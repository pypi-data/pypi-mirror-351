from pydantic import BaseModel
import requests


class API:

    def __init__(self, fqdn: str, bearer: str, insecure: bool = False) -> None:
        self.fqdn = fqdn
        self.headers = {
            "Authorization": f"Bearer {bearer}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        s = "s" if not insecure else ""
        self.baseURL = f"http{s}://{self.fqdn}/api"

    @staticmethod
    def handleResponse(response: requests.Response) -> tuple[bool, dict]:
        if response.status_code in (200, 201):
            return True, response.json()["data"]
        elif response.status_code == 204:
            return True, {}
        else:
            raise RuntimeError(response.json())

    def get(self, endpoint: str) -> dict:
        response = requests.get(f"{self.baseURL}/{endpoint}", headers=self.headers)
        return API.handleResponse(response)[1]

    def update(self, endpoint: str, data: BaseModel) -> dict:
        response = requests.patch(
            f"{self.baseURL}/{endpoint}",
            headers=self.headers,
            json=data.model_dump(exclude_none=True, exclude_defaults=True),
        )
        return API.handleResponse(response)[1]

    def delete(self, endpoint: str, force: bool = False, cascade: bool = False) -> bool:
        if not force and cascade:
            raise ValueError("Cascade can only be true when force is also true")
        parameters = ""
        if force:
            parameters += "?force=true"
            if cascade:
                parameters += "&cascade=true"
        response = requests.delete(
            f"{self.baseURL}/{endpoint}{parameters}", headers=self.headers
        )
        return API.handleResponse(response)[0]

    def add(self, endpoint: str, data: BaseModel) -> dict:
        response = requests.post(
            f"{self.baseURL}/{endpoint}",
            headers=self.headers,
            json=data.model_dump(exclude_none=True, exclude_defaults=True),
        )
        return API.handleResponse(response)[1]
