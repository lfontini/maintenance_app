
import requests
import json

def consultar_servicos(service):
    try:
        headers = {
            'QB-Realm-Hostname': 'ignetworks.quickbase.com',
            'User-Agent': '{User-Agent}',
            'Authorization': 'QB-USER-TOKEN b77d3x_w4i_0_b5vmciccskkpez3b6bnwbum2vpz'
        }

        body = {
            "from": "bmeeuqk9d",
            "select": [7],
            "where": "{21.CT.'%s'}AND{18.CT.'Delivered'}" % service
        }

        url = 'https://api.quickbase.com/v1/records/query'
        r = requests.post(url, headers=headers, json=body)
        
        # Verifica o código de status da resposta
        r.raise_for_status()

        response_json = r.json()

        # Verifica se o campo "data" está vazio
        if not response_json['data']:
            return None
        else:
            # Extrai os valores dos serviços e coloca em uma lista
            services_list = [record['7']['value'] for record in response_json['data']]
            return services_list
    except requests.exceptions.RequestException as e:
        print("Erro de requisição:", e)
        return None
    except json.JSONDecodeError as e:
        print("Erro ao decodificar JSON:", e)
        return None
    except KeyError as e:
        print("Chave não encontrada:", e)
        return None
    except Exception as e:
        print("Ocorreu um erro inesperado:", e)
        return None

# Exemplo de uso da função
service = "RNG.5511.N002"
resultados = consultar_servicos(service)
if resultados is not None:
    print(json.dumps(resultados, indent=4))
else:
    print("Nenhum resultado encontrado ou ocorreu um erro.")
