import os
import json
import glob
import html
import xml.etree.ElementTree as ET
from datetime import datetime
import requests
from time import sleep
from pathlib import Path
from dotenv import load_dotenv


load_dotenv()

GLPI_URL = os.getenv("GLPI_URL")
USER_TOKEN = os.getenv("USER_TOKEN")
APP_TOKEN = os.getenv("APP_TOKEN")
ATTACHMENTS_DIR = os.getenv("ATTACHMENTS_DIR", "Attachments")
PERSONS_PATH = os.getenv("PERSONS_PATH", "adicionais/Person.json")
LOG_DIR = os.getenv("LOG_DIR", "logs")

# ==========================
# CONFIGURAÇÕES SEM .ENV
# ==========================
#GLPI_URL = ""
#USER_TOKEN = ""
#APP_TOKEN = ""
#ATTACHMENTS_DIR = "Attachments"
#PERSONS_PATH = "adicionais/Person.json"
#LOG_DIR = "logs"

# ==========================
# CONFIGURAÇÕES DE LOG
# ==========================

Path(LOG_DIR).mkdir(exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"log_glpi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")


# ==========================
# FUNÇÕES AUXILIARES
# ==========================

def exibir_progresso(atual, total):
    porcentagem = (atual / total) * 100
    print(f"[{atual}/{total}] Progresso: {porcentagem:.2f}%")

def parse_data(timestamp_str):
    try:
        if "T" in timestamp_str:
            return datetime.strptime(timestamp_str.split(".")[0], "%Y-%m-%dT%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
        return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return timestamp_str

def iniciar_sessao():
    headers = {
        "Authorization": f"user_token {USER_TOKEN}",
        "App-Token": APP_TOKEN,
        "Content-Type": "application/json"
    }
    r = requests.get(f"{GLPI_URL}/initSession", headers=headers)
    registrar_log("Iniciar Sessão", f"{GLPI_URL}/initSession", "GET", r.status_code, response_text=r.text)
    if r.status_code == 200:
        print("Sessão iniciada com sucesso!")
        return r.json()["session_token"]
    else:
        print("Erro ao iniciar sessão:", r.status_code, r.text)
        return None

def encerrar_sessao(session_token):
    headers = {
        "App-Token": APP_TOKEN,
        "Session-Token": session_token,
        "Content-Type": "application/json"
    }
    requests.get(f"{GLPI_URL}/killSession", headers=headers)
    print("Sessão encerrada.")

def buscar_usuario_por_email(email, headers):
    r = requests.get(f"{GLPI_URL}/UserEmail?searchText[email]={email}", headers=headers)
    registrar_log("Buscar Usuário", f"{GLPI_URL}/UserEmail?searchText[email]={email}", "GET", r.status_code, response_text=r.text)

    #if len(r.json()) == 0:
    #    print(f"[INFO] Usuário não encontrado: {email}")
    #    return None
    #return r.json()[0]["users_id"]
    try:
        data = r.json()
    except json.JSONDecodeError:
        print(f"[ERRO] Resposta inválida da API para email '{email}'. Status: {r.status_code}")
        print(f"Resposta recebida (não JSON): {r.text[:200]}...")  # Trunca para não poluir terminal
        return None

    if not data:
        print(f"[INFO] Usuário não encontrado: {email}")
        return None

    return data[0].get("users_id")


def criar_usuario_glpi(dados, headers):
    email = dados.get("UserName")
    if not email:
        email = f'no-mail-{dados.get("CorporateName", "invalid").lower() or dados.get("BusinessName", "invalid").lower()}@historicobackup.online'
    email = mail_address_helper(email)
    existing_id = buscar_usuario_por_email(email, headers)
    if existing_id:
        return existing_id

    payload = {
        "input": {
            "name": dados.get("BusinessName", email),
            "realname": dados.get("CorporateName") or dados.get("BusinessName") or email,
            "is_active": 1,
            "nickname": email
        }
    }
    r = requests.post(f"{GLPI_URL}/User", headers=headers, json=payload)
    registrar_log("Criar Usuário", f"{GLPI_URL}/User", "POST", r.status_code, payload, r.text)

    if r.status_code == 201:
        print(f"[INFO] Usuário criado: {email}")
        user_id = r.json()["id"]

        payload_usermail = {
        "input": {
            "users_id": user_id,
            "is_default": 0,
            "is_dynamic": 0,
            "email": email,
            }
        }
        r = requests.post(f"{GLPI_URL}/UserEmail", headers=headers, json=payload_usermail)
        registrar_log("Criar Usuário Email", f"{GLPI_URL}/UserEmail", "POST", r.status_code, payload_usermail, r.text)
        if r.status_code == 201:
            print(f"[INFO] Email adicionado ao usuário {user_id}: {email}")
            return user_id

    print(f"[ERRO] Falha ao criar usuário {email}: {r.status_code} - {r.text}")
    return None

def adicionar_usuario_ao_ticket(ticket_id, user_id, tipo, headers):
    payload = {
        "input": {
            "id": ticket_id,
            "users_id": user_id,
            "type": tipo
        }
    }
    r = requests.post(f"{GLPI_URL}/Ticket_User", headers=headers, json=payload)
    registrar_log("Adicionar Usuário ao Ticket", f"{GLPI_URL}/Ticket_User", "POST", r.status_code, payload, r.text)
    if r.status_code == 201:
        print(f"Usuário {user_id} adicionado ao ticket {ticket_id} como tipo {tipo}")
    else:
        print(f"Erro ao adicionar usuário ao ticket: {r.status_code} - {r.text}")

def carregar_mapeamento_pessoas():
    with open(PERSONS_PATH, "r", encoding="utf-8") as pf:
        persons_map = json.load(pf)["Persons"]
        return {
            person["CodeReference"]: person
            for person in persons_map if person.get("UserName")
        }

def obter_usuario_glpi_por_createdby(createdby_id, headers, id_para_objeto):
    dados = id_para_objeto.get(createdby_id)
    if not dados:
        return 0, 0
    email = dados.get("UserName") or (dados.get("Emails")[0] if dados.get("Emails") else None)
    type_user = dados.get("ProfileType", 2)
    # if not email:
    #     return None, type_user
    email = mail_address_helper(email.strip().replace(" ", "").replace(";", "").replace(",", ""))
    user_id = buscar_usuario_por_email(email, headers)
    if user_id:
        return user_id, type_user

    email2 = mail_address_helper(f'no-mail-{dados.get("CorporateName","invalid").lower() or dados.get("BusinessName", "invalid").lower()}@historicobackup.online')
    user_id2 = buscar_usuario_por_email(email2, headers)
    if user_id2:
        return user_id2, type_user

    return criar_usuario_glpi(dados, headers), type_user

def encontrar_anexo_por_path(path_hash):
    for file in os.listdir(ATTACHMENTS_DIR):
        if file.startswith(path_hash):
            return os.path.join(ATTACHMENTS_DIR, file)
    return None

def adicionar_atores_ticket(ticket_id, users=None, groups=None, headers=None):
    print(f"Adicionando atores ao ticket {ticket_id}...")
    if isinstance(users, list) and len(users) > 0:
        payload_users = {"input": users}
        r = requests.post(f"{GLPI_URL}/Ticket/{ticket_id}/Ticket_User", headers=headers, json=payload_users)
        registrar_log("Adicionar Atores Usuários", f"{GLPI_URL}/Ticket/{ticket_id}/Ticket_User", "POST", r.status_code, payload_users, r.text)
        print(f"Usuários adicionados ao ticket {ticket_id}: {r.status_code}")

    if isinstance(groups, list) and len(groups) > 0:
        payload_groups = {"input": groups}
        r = requests.post(f"{GLPI_URL}/Ticket/{ticket_id}/Group_Ticket", headers=headers, json=payload_groups)
        registrar_log("Adicionar Atores Grupo", f"{GLPI_URL}/Ticket/{ticket_id}/Group_Ticket", "POST", r.status_code, payload_groups, r.text)
        print(f"Grupos adicionados ao ticket {ticket_id}: {r.status_code}")

    print(f"Ajustes de atores realizados para o ticket {ticket_id}!" )

# ==========================
# FUNÇÕES AUXILIARES
# ==========================

def registrar_log(contexto, url, metodo, status, payload=None, response_text=None):
    with open(LOG_FILE, 'a', encoding='utf-8') as log:
        log.write(f"[{contexto}@{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {metodo} {url}\n")
        log.write(f"Status: {status}\n")
        if payload:
            log.write(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}\n")
        if response_text:
            log.write(f"Resposta: {response_text}\n")
        log.write("\n" + ("="*80) + "\n\n")

def mail_address_helper(email:str):
    mail = email.strip().replace(" ", "").replace(";", "").replace(",", "")
    if mail:
        if mail.find("@") == -1:
            mail = f"no-mail-{mail.lower()}@historicobackup.online"
        return mail
    return 'missed-mail@historicobackup.online'

def ticket_ja_importado(numero_ticket, protocolo, headers):
    search_text = f"{numero_ticket} | {protocolo}"
    r = requests.get(
        f"{GLPI_URL}/search/Ticket",
        headers=headers,
        params={
            "criteria[0][field]": 1,
            "criteria[0][searchtype]": "contains",
            "criteria[0][value]": search_text
        }
    )
    registrar_log("Verificar Duplicado", f"{GLPI_URL}/search/Ticket", "GET", r.status_code, response_text=r.text)

    try:
        data = r.json()
        return data.get("totalcount", 0) > 0
    except json.JSONDecodeError:
        print(f"[ERRO] Falha ao interpretar resposta da API. Status: {r.status_code}")
        print(f"Resposta: {r.text[:300]}...")
        return False
    #if r.status_code == 200 and r.json().get("totalcount", 0) > 0:
    #    return True
    #return False

# ==========================
# IMPORTAÇÃO DE CHAMADOS
# ==========================

#def importar_tickets(xml_path, headers, id_para_objeto):
def importar_tickets(xml_path, headers, id_para_objeto, estado_progresso):
    if not os.path.exists(xml_path):
        print(f"Arquivo XML não encontrado: {xml_path}")
        return

    tree = ET.parse(xml_path)
    root = tree.getroot()
    tickets = root.findall("Ticket")
    #total_tickets = len(tickets)

    #for ticket in root.findall("Ticket"):
    for ticket in tickets:
        estado_progresso["atual"] += 1
        exibir_progresso(estado_progresso["atual"], estado_progresso["total"])


        subject = (ticket.findtext("Subject") or "").strip()
        protocolo = (ticket.findtext("Protocol") or "").strip()
        numero = (ticket.findtext("Number") or "").strip()
        status = (ticket.findtext("Status") or "").strip().lower()

        titulo = f"[#{numero} | {protocolo}] {subject}" if protocolo else subject

        if ticket_ja_importado(numero, protocolo, headers):
            print(f"[SKIP] Ticket já existente: {titulo}")
            continue

        created_date = parse_data(ticket.findtext("CreatedDate"))
        modified_date = parse_data(ticket.findtext("LastUpdate"))
        closed_date = parse_data(ticket.findtext("ClosedDate"))
        resolved_date = parse_data(ticket.findtext("ResolvedDate") or ticket.findtext("CanceledDate"))

        requester_code = ticket.findtext("CreatedBy")
        # requester_id = obter_usuario_glpi_por_createdby(requester_code, headers, id_para_objeto)
        requester_data = id_para_objeto.get(requester_code)
        requester_email = requester_data.get("UserName", "movidesk.backup@atendimento.crn9.com.br")



        glpi_status = {
            "novo": 1,
            "em andamento": 2,
            "em espera": 4,
            "resolvido": 5,
            "fechado": 6,
            "cancelado": 5
        }.get(status, 1)

        users_payload = [{
                "tickets_id": 0,
                "users_id": 0,
                "type": 1,
                "use_notification": 0,
                "alternative_email": mail_address_helper(requester_email)
            }]
        # if requester_email:
            # user_id = buscar_usuario_por_email(requester_email, headers)
            # if user_id:
            # users_payload.append({
            #     "tickets_id": 0,
            #     "users_id": 0,
            #     "type": 1,
            #     "use_notification": 0,
            #     "alternative_email": requester_email
            # })


        # Requerente CC
        cc_mail_list = ticket.findtext("Cc")
        if cc_mail_list.find(",") > 0:
            cc_mail_list = cc_mail_list.split(",")
        elif len(cc_mail_list) > 0:
            cc_mail_list = [cc_mail_list]

        for cc_email in cc_mail_list:
            cc_email = cc_email.strip()
            users_payload.append({
                "tickets_id": 0,
                "users_id": 0,
                "type": 1,
                "use_notification": mail_address_helper(cc_email)
            })

        owner_team = (ticket.findtext("OwnerTeam") or "").strip().lower()
        groups_payload = [
            {
                "tickets_id": 0,
                "groups_id": 56,
                "type": 3
            }
        ]
        if owner_team:
            group_id = {
                    "equipe atendimento pf": 2,
                    "crn9-sti": 7,
                    "equipe financeiro": 28,
                }.get(owner_team)
            if group_id:
                groups_payload.append({
                    "tickets_id": 0,
                    "groups_id": group_id,
                    "type": 3
                })

        payload = {
            "input": {
                "name": titulo,
                "status": 1,
                "urgency": 3,
                "itilcategories_id": 0,
                "users_id_recipient": 0,
                "content": ticket.findtext("TicketSubject"),
                "date_creation": created_date,
                "requesttypes_id": 8,
                "type": 2,
                "date": created_date
            }
        }

        r = requests.post(f"{GLPI_URL}/Ticket", headers=headers, json=payload)
        registrar_log("Criar Ticket", f"{GLPI_URL}/Ticket", "POST", r.status_code, payload, r.text)
        if r.status_code != 201:
            print(f"Erro ao criar ticket '{subject}': {r.status_code} - {r.text}")
            continue

        ticket_id = r.json().get("id")
        print(f"Ticket criado: GLPI:{ticket_id} [#{numero} | {protocolo}] - {subject}")

        for user_payload in users_payload:
                user_payload["tickets_id"] = ticket_id
        for group_payload in groups_payload:
            group_payload["tickets_id"] = ticket_id

        adicionar_atores_ticket(ticket_id, users=users_payload, groups=groups_payload, headers=headers)


        for action in ticket.findall("Action"):
            descricao_raw = action.findtext("Description", "")
            descricao = html.unescape(descricao_raw)
            acao_data = parse_data(action.findtext("CreatedDate"))
            createdby_id = action.findtext("CreatedBy")
            user_glpi_id, user_type = obter_usuario_glpi_por_createdby(createdby_id, headers, id_para_objeto)

            if user_type == 3:
                adicionar_atores_ticket(ticket_id, users=[
                    {
                        "tickets_id": ticket_id,
                        "users_id": user_glpi_id,
                        "type": 2,
                        "use_notification": 0,
                    }
                ], headers=headers)
                registrar_log("Adicionar Atores Usuário", f"{GLPI_URL}/Ticket/{ticket_id}/Ticket_User", "POST", r.status_code, payload=users_payload, response_text="")
                print(f"Adicionando usuário {user_glpi_id} como técnico ao ticket {ticket_id} >> status {r.status_code}")
            anexo_path = action.find("TicketActionAttachment/Path")
            anexo_local = encontrar_anexo_por_path(anexo_path.text) if anexo_path is not None else None

            # action_actor_data = id_para_objeto.get(createdby_id)
            # action_actor_email = action_actor_data.get("UserName", "movidesk.backup.actor@atendimento.crn9.com.br")


            followup_payload = {
                "input": {
                    "itemtype": "Ticket",
                    "items_id": ticket_id,
                    # "content": f'{action_actor_email} realizou a seguinte ação: \n\n {descricao}'
                    "content": descricao,
                    "is_private": 0,
                    "date_creation": acao_data,
                    "date_mod": acao_data,
                    "users_id": user_glpi_id
                }
            }

            r = requests.post(f"{GLPI_URL}/ITILFollowup", headers=headers, json=followup_payload, timeout=60)
            registrar_log("Adicionar Acompanhamento", f"{GLPI_URL}/ITILFollowup", "POST", r.status_code, followup_payload, r.text)
            print(f"Acompanhamento adicionado ao ticket {ticket_id}")

            if anexo_local:
                sleep(2)
                files = {
                    'uploadManifest': (None, json.dumps({
                        "input": {
                            "itemtype": "Ticket",
                            "items_id": ticket_id,
                            "name": os.path.basename(anexo_local),
                            "comment": "Importado via API"
                        }
                    })),
                    'filename[]': open(anexo_local, 'rb')
                }

                headers_upload = {
                    "App-Token": APP_TOKEN,
                    "Session-Token": session_token
                }

                r = requests.post(f"{GLPI_URL}/Document", headers=headers_upload, files=files)
                # registrar_log("Enviar Anexo", f"{GLPI_URL}/Document", "POST", r.status_code, files, r.text)
                print(f"Anexo enviado: {anexo_local} status_code: {r.status_code}")
                print(f"Resposta da API para documento enviado: {r.text}")
        payload_update = {
            "input": {
                "id": ticket_id,
                "name": titulo,
                "status": glpi_status,
                # "date_mod": modified_date,
                "solvedate": resolved_date,
                # "closedate": closed_date
            }
        }

        r = requests.put(f"{GLPI_URL}/Ticket/{ticket_id}", headers=headers, json=payload_update)
        registrar_log("Atualizar Ticket", f"{GLPI_URL}/Ticket/{ticket_id}", "PUT", r.status_code, payload_update, r.text)
        if r.status_code == 200:
            print(f"Atualização de chamado '{titulo}': solução = {resolved_date}, fechamento = {closed_date}")
        else:
            print(f"Erro ao atualizar datas do chamado '{titulo}': {r.status_code} - {r.text}")

# ==========================
# EXECUÇÃO PRINCIPAL
# ==========================

if __name__ == "__main__":
    session_token = iniciar_sessao()
    if session_token:
        HEADERS = {
            "App-Token": APP_TOKEN,
            "Session-Token": session_token,
            "Content-Type": "application/json"
        }

        try:
            id_para_email = carregar_mapeamento_pessoas()

            # 📦 Etapa 1: Contar todos os tickets em todos os arquivos XML
            total_tickets = 0

            xml_files = sorted(glob.glob("*.xml"))
            print(f"Iniciando contagem de arquivos XML...")
            print(f"Arquivos encontrados: {len(xml_files)}")

            for xml_file in xml_files:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                ticket_count = len(root.findall("Ticket"))
                total_tickets += ticket_count
                print(f" → {xml_file}: {ticket_count} tickets")

            print(f"Total de tickets a importar: {total_tickets}")
            print("=" * 60)

            # Inicializa progresso global
            progresso = {"atual": 0, "total": total_tickets}

            # 📦 Etapa 2: Importar com progresso global
            for xml_file in xml_files:
                print(f"Importando: {xml_file}")
                importar_tickets(xml_file, HEADERS, id_para_email, progresso)

            #for xml_file in glob.glob("*.xml"):
            #    print(f"Importando: {xml_file}")
            #    importar_tickets(xml_file, HEADERS, id_para_email)
        finally:
            encerrar_sessao(session_token)