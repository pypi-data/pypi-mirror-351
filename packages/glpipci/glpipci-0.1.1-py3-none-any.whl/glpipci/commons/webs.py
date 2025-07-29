from dotenv import load_dotenv
import os
import httpx


class BasicAuth:
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password

    @property
    def auth(self) -> str:
        return httpx.BasicAuth(username=self.username, password=self.password)


class GlpiBasicApiClient:
    """
    A class representing a basic API client for GLPI (Gestionnaire Libre de Parc Informatique).
    This class is used to define the basic attributes of an API client.
    """
    load_dotenv()
    _ENV_API_ENDPOINT = os.getenv('GLPI_API_ENDPOINT', 'http://localhost:8090/apirest.php')

    def __init__(
            self,
            username: str | None = None,
            password: str | None = None,
            server_endpoint: str | None = None,
            app_token: str | None = None,
            user_token: str | None = None,
            session_token: str | None = None,
    ) -> None:
        self.api_server_endpoint = server_endpoint or self._ENV_API_ENDPOINT
        self.api_client = httpx.Client()
        if username and password:
            self.__basic_auth: BasicAuth = BasicAuth(username=username, password=password)
            self.api_client = httpx.Client(auth=self.__basic_auth.auth)

    def make_get(self, *args, **kwargs):
        kwargs['headers'] = self.auth_headers
        return self.api_client.get(*args, **kwargs)

    def make_post(self, *args, **kwargs):
        kwargs['headers'] = self.auth_headers
        return self.api_client.post(*args, **kwargs)

    def make_put(self, *args, **kwargs):
        kwargs['headers'] = self.auth_headers
        return self.api_client.put(*args, **kwargs)

    def make_delete(self, *args, **kwargs):
        kwargs['headers'] = self.auth_headers
        return self.api_client.delete(*args, **kwargs)

    def make_patch(self, *args, **kwargs):
        kwargs['headers'] = self.auth_headers
        return self.api_client.patch(*args, **kwargs)


class GlpiBasicItem:
    """
    A class representing a basic item in GLPI (Gestionnaire Libre de Parc Informatique).
    This class is used to define the basic attributes of an item.
    """

    def __init__(self, api_client: GlpiBasicApiClient, **kwargs) -> None:
        """
        Initialize the GlpiBasicItem with the given attributes.

        :param kwargs: The attributes of the item.
        """
        self.api_object_endpoint = ''
        self.api_client = api_client

    @property
    def item_endpoint(self):
        return self.api_client.api_server_endpoint + self.api_object_endpoint