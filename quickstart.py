import datetime
import os.path
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

def main():
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("calendar", "v3", credentials=creds)
    return service

  except HttpError as error:
    print(f"An error occurred: {error}")
    return False


servico = main()

gestores = {
    "lydia":"1a1f567e5951e74ab4b4fdeb129c25a6cd6d8516089ee27a4dc5d6cb895666de@group.calendar.google.com",
    "marco":"9eacdefd602921c3e2bd9a508284dff22c6fe2a1b76d1af6792f415481552baf@group.calendar.google.com",
    "kevyn":"f16024f5fe6d402bb81cd3d8e7489ad9776a0cadd3b646bbb771b8228fe57a6d@group.calendar.google.com",
    "lucas":"06cea7136bdd5bb2f04f351d0bb04e7041de25a9859ccf0ec397324e464fc4c6@group.calendar.google.com",
    "victor":"84fe9e55a28112857453617136ed1af2c81f929c6ab025c4b07c3b6e02589155@group.calendar.google.com",
    "ana":"8565d35d363ba5608ca89a0796e6d059b460361628bf78c2ba49f437c3f789f1@group.calendar.google.com",
    "atd_jud":"62de3566935f607f666a95cbb93743b5121fa66cfe2a79dc3208057d2cbafcb2@group.calendar.google.com",
    "yan":"0a73de185c45756b27d12632896dfeb9d3f409b0e3e98efb85d03dc49ad92ce5@group.calendar.google.com",
    "weriqui":"primary"
}
agenda_principal = '785ff172ceec6bbfa21495a4bde63067e43d860cd6934112f0b6a9289b4f1b91@group.calendar.google.com'


def verificar_disponibilidade_advogado(gestor:str, evento_principal:dict,servico=servico):
    if gestor == "atd_jud":
        return True
    elif servico:
        calendario_id_advogado = gestores[gestor]
        fuso_brasilia = pytz.timezone("America/Sao_Paulo")  # Define o fuso horário de Brasília
        horario_reuniao_inicio = datetime.datetime.fromisoformat(evento_principal['start'].get('dateTime', evento_principal['start'].get('date')))
        horario_reuniao_fim = datetime.datetime.fromisoformat(evento_principal['end'].get('dateTime', evento_principal['end'].get('date')))

        # Depois, converte para o fuso horário de Brasília
        horario_reuniao_inicio = horario_reuniao_inicio.astimezone(fuso_brasilia)
        horario_reuniao_fim = horario_reuniao_fim.astimezone(fuso_brasilia)

        # Converte para strings no formato RFC3339
        timeMin = horario_reuniao_inicio.isoformat()
        timeMax = horario_reuniao_fim.isoformat()
        # Lista os eventos no calendário do advogado no intervalo de interesse
        eventos = servico.events().list(calendarId=calendario_id_advogado, timeMin=timeMin, timeMax=timeMax, singleEvents=True).execute()

        # Verifica se há eventos que se sobrepõem ao horário proposto
        for evento in eventos.get('items', []):
            inicio_evento = datetime.datetime.fromisoformat(evento['start'].get('dateTime', evento['start'].get('date')))
            fim_evento = datetime.datetime.fromisoformat(evento['end'].get('dateTime', evento['end'].get('date')))

            # Se houver sobreposição, o advogado não está disponível
            if not (inicio_evento >= horario_reuniao_fim or fim_evento <= horario_reuniao_inicio):
                return False  # Indisponível

        return True  # Disponível
    else:
        print("Falha ao autenticar com o Google Calendar API.")
        return False
    
def copiar_evento_para_advogado(evento_id, gestor,servico=servico):
    if servico:
        calendario_destino = gestores[gestor]
        evento = servico.events().get(calendarId=agenda_principal, eventId=evento_id).execute()
        # Insere o evento no calendário do advogado
        evento_copiado = servico.events().insert(calendarId=calendario_destino, body=evento).execute()
        print(f"Evento copiado para o calendário do advogado: {gestor}")
        
    else:
        print("Falha ao autenticar com o Google Calendar API.")
        return 'erro'


def buscar_eventos_por_criador_e_nome(email_criador, nome_evento, nome_criador=None, servico=servico):
    if servico:
        calendario_id = agenda_principal
        eventos_filtrados = []
        pagina_token = None
        agora_utc = datetime.datetime.now(pytz.UTC)
        while True:
            eventos = servico.events().list(calendarId=calendario_id, pageToken=pagina_token, singleEvents=True, timeMin=agora_utc.isoformat()).execute()

            for evento in eventos.get('items', []):
                criador_email = evento.get('creator', {}).get('email', '')
                criador_nome = evento.get('creator', {}).get('displayName', '')
                evento_nome = evento.get('summary', '')
                # Converte a string de data de início do evento para um objeto datetime
                data_evento_inicio = datetime.datetime.fromisoformat(evento['start'].get('dateTime', evento['start'].get('date')).rstrip('Z')).replace(tzinfo=pytz.UTC)

                # Verifica se o evento ocorre a partir do dia atual e corresponde aos demais critérios
                if data_evento_inicio >= agora_utc and criador_email == email_criador and (nome_criador is None or criador_nome == nome_criador) and nome_evento in evento_nome:
                    eventos_filtrados.append(evento)

            pagina_token = eventos.get('nextPageToken')
            if not pagina_token:
                break

        # Garante que a lista não está vazia antes de tentar acessar o primeiro elemento
        if eventos_filtrados:
            return eventos_filtrados[0]
        else:
            return False
    else:
        return False
