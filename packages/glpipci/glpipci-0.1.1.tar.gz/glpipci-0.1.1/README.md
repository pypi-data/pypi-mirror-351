
# glpipci - GLPI Python Comunicator Interface - [unofficial]


![PyPI](https://img.shields.io/pypi/v/glpipci) ![Python Version](https://img.shields.io/pypi/pyversions/glpipci) ![License](https://img.shields.io/pypi/l/glpipci) ![Beta](https://img.shields.io/badge/status-beta-yellow)

Um cliente Python para a API do GLPI.

## Instalação

Para instalar o pacote, use o seguinte comando:

```bash
pip install glpipci
```

## Uso

### Básico

Exemplo de como usar o pacote

```python
from glpipci.comunicator.v10_0.api import GLPIApiClient

client = GLPIApiClient(username="admin", password="password")
response = client.make_get("http://localhost:8090/apirest.php/some_endpoint")
print(response.json())
```

### Variáveis de ambiente

Variáveis de ambiente (export ou arquivo .env)

```env
GLPI_URL=https://localhost/apirest.php
USER_TOKEN=FooUserTokenFOOuserTokenFoOuSeRtOkEn
APP_TOKEN=fOOTokenFooTokenFooTokenFooToken
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123123123123/fknsoaoknasfoknfasokafsnonkfsoknsfakonfs
ATTACHMENTS_DIR=Attachments
PERSONS_PATH=adicionais/Person.json
LOG_DIR=logs
```

Código:

```python
from glpipci.comunicator.v10_0.api import GLPIApiClient
client = GLPIApiClient(username="admin", password="password")

from glpipci.comunicator.v10_0.endpoints.tickets.core import  GlpiTickets
tickets = GlpiTickets(
    api_client=client
)

response = tickets.get_tickets()

print(response.json())
```

## Contribuição
Se você deseja contribuir para este projeto, siga estas etapas:

1. Faça um fork do repositório.
2. Crie uma nova branch (`git checkout -b feature-branch`).
3. Faça suas alterações e commit (`git commit -m 'Add some feature'`).
4. Envie para o repositório remoto (`git push origin feature-branch`).
5. Crie um novo Pull Request.
6. Aguarde a revisão e feedback.


## Licença
Este projeto está licenciado sob a Licença MIT. Veja o arquivo [LICENSE](LICENSE.txt) para mais detalhes.


## Extras

```shell
export PYTHONPATH=$PYTHONPATH:/home/tlsabara/repos/tlsabara/pyglpi/glpipci
```