import sys
sys.path.append('/home/tlsabara/repos/tlsabara/pyglpi/glpipci')

from glpipci.comunicator.v10_0.api import GLPIApiClient
from glpipci.comunicator.v10_0.endpoints.tickets.core import GlpiTickets, GlpiTicket

def list_tickets():
    client = GLPIApiClient(
        username="glpi",
        password="glpi",
        server_endpoint="http://localhost:8090/apirest.php",
        app_token="HNVEtWFQTC7H6SlU6K1tZmItCEYcHE7HZANdqO5j",
    )
    # client._init_session()
    # tickets = client.make_get(
    #     client.api_server_endpoint + '/Ticket/1'
    # ).json()

    tickets_operator = GlpiTickets(
        api_client=client,
    )

    tickets = tickets_operator.get_tickets()

    if not tickets:
        print("No tickets found.")
        return

    for ticket in tickets:
        print("?")
        print(ticket)

if __name__ == "__main__":
    list_tickets()