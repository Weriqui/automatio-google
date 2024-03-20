from flask import Flask, request, jsonify
import requests
import json
from distribuicao import distribui
from quickstart import copiar_evento_para_advogado as  copiar_agenda
from quickstart import buscar_eventos_por_criador_e_nome as busca_evento
import datetime
from datetime import timedelta
import time

app = Flask(__name__)
assessores = [14214740,15259883,15518207,15393027,13296123,15259894]
advs = {
    14213783:"kevyn",
    14213794:"lucas",
    14330372:"ana",
    14259807:"lydia",
    14330361:"victor",
    16413097:"yan",
    14284568:"weriqui"
    
}
advs_id = {
    "kevyn":14213783,
    "lucas":14213794,
    "ana":14330372,
    "lydia":14259807,
    "victor":14330361,
    "yan":16413097,
    "weriqui":14284568
}

advs_wpp = {
    "ana":"5562981186771",
    "lydia":"5511972901916",
    "victor":"5521992402279",
    "kevyn":"5511918739557",
    "lucas":"5548992103237",
    "marco":"5511989848487"
}

def dia_reuniao(dia:str):
    s = dia.split("-")
    resultado = f"Reunião Agedada para o dia {s[-1]}/{s[1]}"
    return resultado

def fusohorario(uf):
    dicionario = {
        "AC":-2,
        "AM":-1,
        "MT":-1,
        "MS":-1,
        "RO":-1,
        "RR":-1
    }
    if uf in dicionario.keys():
        return f'O estado agendado tem um fuso horario de {dicionario[uf]} horas'
    else:
        return False

def envia_mensagem(mensagem:str)->None:
    url = "https://app.whatsgw.com.br/api/WhatsGw/Send"
    payload = json.dumps({
        "apikey": "fcb93c32-f93c-4d3f-8546-583472643bb0",
        "phone_number": "5548999425440",
        "contact_phone_number": "120363247313592309",
        "message_type": "text",
        "message_body": mensagem,
        "check_status": "1",
        "message_to_group": 1
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    
def mensagem_agenda(mensagem:str,numero:str)->None:
    url = "https://app.whatsgw.com.br/api/WhatsGw/Send"
    payload = json.dumps({
        "apikey": "fcb93c32-f93c-4d3f-8546-583472643bb0",
        "phone_number": numero,
        "contact_phone_number": "120363247313592309",
        "message_type": "text",
        "message_body": mensagem,
        "check_status": "1",
        "message_to_group": 1
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

estados = ["AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"]

def apontaErro(assessor:str, evento:str,titulo:str,criador:int,horario:bool):
    if 'http' not in evento:
        if criador in assessores:
            envia_mensagem(f"{assessor} Criou uma reunião e não colocou o Link na descrição\n{titulo}")
        return True

    if (titulo[:2] not in estados) or (titulo == "Reunião"):
        if criador in assessores:
            envia_mensagem(f"{assessor} Criou uma reunião e não colocou o estado no titulo\nTitulo da atividade: {titulo}")
        return True
    if horario == False:
        if criador in assessores:
            envia_mensagem(f"{assessor} Criou uma reunião e não inseriu o horário\nTitulo da atividade: {titulo}")
        return True
        

def alterar_evento(id,descricao):
    url = f"https://api.pipedrive.com/v1/activities/{id}?api_token=6c7d502747be67acc199b483803a28a0c9b95c09"

    payload = json.dumps({
    "public_description": descricao
    })
    headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)

def procura_evento(id):
    url = f"https://api.pipedrive.com/v1/activities/{id}?api_token=6c7d502747be67acc199b483803a28a0c9b95c09"

    payload = {}
    headers = {
    'Accept': 'application/json'
    }

    response = requests.request("GET", url, headers=headers, data=payload).json()

    return response

def horario(hora:str):
    horario_obj = datetime.datetime.strptime(hora, "%H:%M")
    horario_modificado = horario_obj - timedelta(hours=3)
    horario_final = horario_modificado.strftime("%H:%M")
    return horario_final

def codificar_para_unicode(texto):
    # Substitui caracteres específicos e adiciona marcações HTML
    texto_codificado = texto
    texto_codificado = texto_codificado.replace("\n", "<br>\n")  # Adiciona marcação HTML para nova linha.
    
    # Substituição de caracteres especiais (acentuados) por sequências Unicode
    substituicoes = {
        "á": "\\u00e1",
        "é": "\\u00e9",
        "í": "\\u00ed",
        "ó": "\\u00f3",
        "ú": "\\u00fa",
        "ç": "\\u00e7",
        "ã": "\\u00e3",
        "õ": "\\u00f5",
        "â": "\\u00e2",
        "ê": "\\u00ea",
        "î": "\\u00ee",
        "ô": "\\u00f4",
        "û": "\\u00fb",
        "à": "\\u00e0",
        "è": "\\u00e8",
        "ì": "\\u00ec",
        "ò": "\\u00f2",
        "ù": "\\u00f9"
    }
    for original, unicode in substituicoes.items():
        texto_codificado = texto_codificado.replace(original, unicode) 
    return texto_codificado

def transferir_negocio(id:int,novo_proprietario:int):
    url = f"https://api.pipedrive.com/v1/deals/{id}?api_token=6c7d502747be67acc199b483803a28a0c9b95c09"

    payload = json.dumps({
        "user_id": novo_proprietario
    })
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Cookie': '__cf_bm=k1e34Ywsk1CCGnXCMaK..D9e8bd05qBOeVTHoxowfUE-1710952674-1.0.1.1-zaq1XkdP.9VZdCCcIKG1m0SXUjME_NKVJKj80g0uFx_.ZO8MOXEQ.6UNSQPDzSrdQZHoxLvQzeFqMmzc_68how'
    }

    response = requests.request("PUT", url, headers=headers, data=payload)



produtos = {
    19: 'TAX SN',
    20: 'TI - Transação Individual',
    21: 'COP',
    23: 'Score',
    24: 'Holding',
    25: 'LVE',
    26: 'RB',
    27: 'Redução Parcelamentos PJ',
    44: 'MS',
    45: 'P2 - Auditoria',
    49: 'TAX (LP)',
    50: 'TAX (LR)',
    52: 'Transação PF',
    63: 'Redução Parcelamentos (p/TAX)',
    66: 'SN Dívida Ativa',
    67: 'PRF (Débitos ajuizados PJ)',
    69: 'Alíquota Zero',
    71: 'MS SN',
    72: 'Redução PERT PJ',
    73: 'Redução PERT PF',
    74: 'Termo exclusão PERT',
    75: 'Redução PERT (Cliente VBB)',
    79: 'Redução de parcelamento (Cliente VBB)',
    80: 'PRF PF (CDAs Recentes)',
    81: 'Crédito vs Débito (Supermercado LR)',
    82: 'Crédito vs Débito (Construtora LR)',
    83: 'Crédito vs Débito (Transportadora LR)',
    90: 'PS CORP',
    95: 'Franquia (contador)',
    98: 'PS Corp (devedor)',
    100: 'Parcelas fixas',
    101: 'Transação Estadual SP',
    107: 'Redução Parcelamentos PF',
    108: 'Pequeno Valor PF',
    109: 'Pequeno Valor PJ',
    114: 'TIS - Transação Individual Simplificada',
    115: 'Equiparação Hospitalar',
    116: 'PS Corp (mercado aberto)',
    134: 'PENHORA DE FATURAMENTO',
    135: 'REVISÃO DE CAPAG',
    146: 'Redução Transação PJ',
    148: 'PENHORA FATURAMENTO - DEVEDOR',
    149: 'COMPRA DE DÍVIDA',
    152: 'REDUÇÃO TRANSAÇÃO PJ - EXCLUSÃO'
}

def consulta_negocio(id:int) -> dict:

    url = f"https://api.pipedrive.com/v1/deals/{id}?api_token=6c7d502747be67acc199b483803a28a0c9b95c09"

    payload = {}
    headers = {
    'Accept': 'application/json',
    'Cookie': '__cf_bm=8LNq6k27OTOnf8nnYEG3kOTmvkPnBde3Gmn.eJDaz2E-1710787958-1.0.1.1-C6Whlqw_EqMepoZN.sbWns.xQ3AHBvuJrovV_CsdutpFAbFc2dpqQZYalWg8TB1fEeEQcX19vbHlpsGKCI_b6Q'
    }

    response:json = requests.request("GET", url, headers=headers, data=payload).json()

    produto:int = int(response["data"]["5fca6336de210f847b78ce5fd7de950530e26e94"])
    valor_beneficio:int = int(response["data"]["2d242d06151f4dab1bbebe3a6a1de1aa1ccee6cb"]) if response["data"]["2d242d06151f4dab1bbebe3a6a1de1aa1ccee6cb"] is not None else 0
    saida = {
        "valor_beneficio":valor_beneficio,
        "produto":produtos[produto]
    }
    return saida

@app.route('/webhook', methods=['POST'])
def webhook():
    print("Notificação de webhook recebida.")
    pesquisa:json = request.get_json()
    procurar:str = pesquisa["meta"]["id"]
    data:json = procura_evento(procurar)
    print(data)
    if data["data"]["type"] == "meeting":

        id_evento:int = data["data"]["id"]
        id_negocio:int = data["data"]["deal_id"]
        key_adress:str = list(data["related_objects"]["organization"].keys())[0]
        key_email:str = list(data["related_objects"]["user"].keys())[0]
        email_criador:str = data["related_objects"]["user"][key_email]["email"]
        print(data["related_objects"]["organization"][key_adress])
        uf:str = data["related_objects"]["organization"][key_adress]["address"].split(',')[1].strip() if len(data["related_objects"]["organization"][key_adress]["address"].split(',')) > 1 else data["related_objects"]["organization"][key_adress]["address"]
        criador_agenda:str = data["data"]["owner_name"]
        descricao_evento:str = data["data"]["public_description"]
        titulo_agenda:str = data["data"]["subject"]
        data_evento = dia_reuniao(data["data"]["due_date"])
        horario_evento = horario(data["data"]["due_time"]) if data["data"]["due_time"] != "" else False
        bp:dict = consulta_negocio(id_negocio)
        nome_produto:str = bp["produto"]
        valor_beneficio:int = bp["valor_beneficio"]
        id_criador:int = data["data"]["created_by_user_id"]
        fuso:str|bool = fusohorario(uf)
        tem_erro = apontaErro(criador_agenda,descricao_evento,titulo_agenda,id_criador,horario_evento)
        if tem_erro:
            time.sleep(60)
            data:json = procura_evento(procurar)
            id_evento:int = data["data"]["id"]
            id_negocio:int = data["data"]["deal_id"]
            key_adress:str = list(data["related_objects"]["organization"].keys())[0]
            key_email:str = list(data["related_objects"]["user"].keys())[0]
            email_criador:str = data["related_objects"]["user"][key_email]["email"]
            uf:str = data["related_objects"]["organization"][key_adress]["address"].split(',')[1].strip()
            criador_agenda:str = data["data"]["owner_name"]
            descricao_evento:str = data["data"]["public_description"]
            titulo_agenda:str = data["data"]["subject"]
            data_evento = dia_reuniao(data["data"]["due_date"])
            horario_evento = horario(data["data"]["due_date"]) if data["data"]["due_date"] != "" else False
            bp:dict = consulta_negocio(id_negocio)
            nome_produto:str = bp["produto"]
            valor_beneficio:int = bp["valor_beneficio"]
            id_criador:int = data["data"]["created_by_user_id"]
            fuso:str|bool = fusohorario(uf)
        if fuso:
            texto =f"\n{fuso}\n{nome_produto}\n"
            alterar = codificar_para_unicode(texto)

            if "\u2500<br>" in descricao_evento:
                nova_descricao = descricao_evento.replace("\u2500<br>",f"\u2500<br>{alterar}")
                alterar_evento(id_evento,nova_descricao)
            else:
                alterar_evento(id_evento,alterar)
        else:
            texto =f"\n{nome_produto}\n"
            alterar = codificar_para_unicode(texto)
            if "\u2500<br>" in descricao_evento:
                nova_descricao = descricao_evento.replace("\u2500<br>",f"\u2500<br>{alterar}")
                alterar_evento(id_evento,nova_descricao)
            else:
                alterar_evento(id_evento,alterar)
                
        if id_criador in assessores:
            transfere = distribui(valor_beneficio,uf,titulo_agenda,email_criador)
            if transfere != 'erro':
                if transfere == "atd_jud":
                    transferir_negocio(id_negocio,15259883)
                else:
                    transferir_negocio(id_negocio,advs_id[transfere])
                    if horario_evento:
                        mensagem = f"{data_evento} as {horario_evento}\n{titulo_agenda}"
                    else:
                        mensagem = f"{data_evento}\n{titulo_agenda}"
                    mensagem_agenda(mensagem,advs_wpp[transfere])
            return jsonify({"status": "Verifição realizada com sucesso"})
        else:
            evento = busca_evento(email_criador,titulo_agenda)
            copiar_agenda(evento["id"],advs[id_criador])
            transferir_negocio(id_negocio,id_criador)
            return jsonify({"status": "Verifição realizada com sucesso"})
    else:
        return jsonify({"status": "Não é reunião"})

    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)