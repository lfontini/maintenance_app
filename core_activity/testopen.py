from openai import OpenAI

# Configurando o cliente OpenAI
openai_client = OpenAI(
    api_key="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")


# Atualizando o prompt para obter respostas mais específicas
inst = """
Você está encarregado de responder a clientes  janelas de manutenção programadas. Por favor, forneça respostas concisas e relevantes. Caso o cliente não autorize a janela ou questione detalhes, peça que revejam os planos e considerem opções menos impactantes. Certifique-se de incluir informações sobre data, horário e duração da manutenção. Se o cliente não fornecer uma resposta clara, indique que verificará e retornará posteriormente. Mantenha a linguagem formal em português, inglês ou espanhol, dependendo do idioma da comunicação. Evite respostas desnecessárias ou informações fora do escopo de manutenção de telecomunicações. O contexto inclui um ticket de manutenção aberto. Agradeça pela compreensão do cliente.

---

Objetivo da Conversa: Ajudar a responder sobre janelas de manutenção em inglês, português e espanhol, dependendo do input.
Contexto Específico: Apenas saber se o cliente autoriza ou questiona a janela.
Detalhes Adicionais: Em manutenções programadas, enviamos primeiro um e-mail para informar a janela e tratamos qualquer retorno do cliente.
Preferências de Resposta: Sim, horário, autorização da janela; caso não responda, que verifique e retorne posteriormente.
Idioma de Preferência: Resposta no idioma da informação fornecida, com o contexto de um ticket de manutenção aberto.
Nível de Detalhes: Linguagem formal.
Preferências de Resposta: Respostas concisas.
Feedback Instantâneo: Respostas concisas.
Tópicos Sensíveis: Não responder se não houver informações relevantes.
Tempo de Resposta: Dentro do escopo de janelas de manutenção de sistemas de telecomunicações e redes.
"""

texto = ''' 

Dear GTT Communications team,

This ticket is to notify you of maintenance activities we will be performing on our network which will affect your service with sporadic flaps or outage for the following period of time.

Starting Date/Time: 23/11/2023 04:00 UTC
Finalizing Date/Time: 23/11/2023 05:00 UTC
Estimated downtime: 01:00 hours

Activity: Crucial - Maintenance Window in order to improve network
Location: São Paulo, Brazil

Affected Service(s):
GTT.5511.A018

Kind Regards.

'''


def obter_resposta_openai(prompt, client):

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": texto},
            {"role": "system", "content": inst},
            {"role": "user", "content": prompt}
        ]
    )
    print(completion)
    return completion.choices[0].message.content


# Exemplo de interação
print("Olá! Eu sou seu assistente. Digite 'sair' para encerrar.")

while True:
    pergunta = input("Você: ")
    if pergunta.lower() == 'sair':
        break

    resposta = obter_resposta_openai(pergunta, openai_client)
    print(f"Assistente: {resposta}")

print("Até mais!")
