from quickstart import verificar_disponibilidade_advogado as gestor_disponivel
from quickstart import copiar_evento_para_advogado as  copiar_agenda
from quickstart import buscar_eventos_por_criador_e_nome as busca_evento


estado_preferencia = ["SP","MG","GO","DF","MT","MS","RJ","ES","BA","RS","SC","PR"]
ordem_preferencia = ["kevyn","lucas","lydia","victor","ana","atd_jud"]
gestor_uf={
    "SP":["lydia","marco","kevyn","lucas","victor","ana","atd_jud"],
    "MG":["lydia","marco","kevyn","lucas","victor","ana","atd_jud"],
    "GO":["ana","lydia","kevyn","lucas","victor","atd_jud"],
    "DF":["ana","lydia","kevyn","lucas","victor","atd_jud"],
    "MT":["ana","lydia","kevyn","lucas","victor","atd_jud"],
    "MS":["ana","kevyn","lucas","lydia","victor","atd_jud"],
    "RJ":["victor","kevyn","lucas","lydia","ana","atd_jud"],
    "ES":["victor","kevyn","lucas","lydia","ana","atd_jud"],
    "BA":["victor","kevyn","lucas","lydia","ana","atd_jud"],
    "RS":ordem_preferencia,
    "SC":ordem_preferencia,
    "PR":ordem_preferencia,
}

def distribui(valor_do_beneficio:int,uf:str,titulo:str,criador:str):
    try:
        evento:dict = busca_evento(criador, titulo)
        if evento:
            if valor_do_beneficio >= 1000000:
                for i in ordem_preferencia:
                    if gestor_disponivel(i,evento) == True:
                        copiar_agenda(evento["id"],i)
                        return i
            else:
                if uf in estado_preferencia:
                    for i in gestor_uf[uf]:
                        if gestor_disponivel(i,evento) == True:
                            copiar_agenda(evento["id"],i)
                            return i
                else:
                    for i in ordem_preferencia:
                        if gestor_disponivel(i,evento) == True:
                            copiar_agenda(evento["id"],i)
                            return i
        else:
            print("evento não encontado")
            return 'erro'
    except KeyError as e:
        print(f"O erro: {e}")
        return 'erro'
