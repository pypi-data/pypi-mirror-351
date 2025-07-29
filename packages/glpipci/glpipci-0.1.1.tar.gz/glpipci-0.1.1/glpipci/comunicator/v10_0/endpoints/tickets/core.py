from glpipci.comunicator.v10_0.api import GLPIApiClient

CONTEXT_URI_PATTERN = "/Ticket"

class GlpiTicket:
    """
    Class to manage a ticket in GLPI.
    """
    def __init__(self, id: str, api_client: GLPIApiClient) -> None:
        self.ticket_id = id
        self.api_client = api_client
        self.api_object_endpoint = f"/{CONTEXT_URI_PATTERN}/{self.ticket_id}"

        # TODO: Trazer os atributod de um ticket para esta classe

    def get_ticket(self) -> dict:
        """
        Get the ticket details.
        """
        response = self.api_client.get(self.api_object_endpoint, headers=self.api_client.auth_headers)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def search_tickets(self, search_by: str | None = None, search_value: str | None = None, search_string: str | None = None) -> list[dict]:
        if search_by is None:
            response = self.api_client.make_get(
                self.api_object_endpoint + f"/?searchText[{search_string}]={search_value}",
                headers=self.api_client.auth_headers
            )


class GlpiTickets:
    """
    Class to manage tickets in GLPI.
    """

    def __init__(self, api_client) -> None:
        self.api_client = api_client
        self.api_object_endpoint = f"/{CONTEXT_URI_PATTERN}"

    def get_tickets(self) -> list[dict]:
        """
        Get the lifst of tickets.
        """
        endpoint = self.api_client.api_server_endpoint + self.api_object_endpoint
        response = self.api_client.make_get(endpoint)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")
