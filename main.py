import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

with open("prompts/a_BIBLIOTECA.txt", "r", encoding="utf-8") as f:
    prompt_biblioteca = f.read()

with open("prompts/a_PREFEITURA.txt", "r", encoding="utf-8") as f:
    prompt_prefeitura = f.read()

with open("prompts/a_LABORATORIOS.txt", "r", encoding="utf-8") as f:
    prompt_laboratorios = f.read()

with open("prompts/a_CENTRAL.txt", "r", encoding="utf-8") as f:
    prompt_central = f.read()

PROMPTS = {
    "Biblioteca": prompt_biblioteca,
    "Prefeitura": prompt_prefeitura,
    "Laboratórios": prompt_laboratorios,
    "Central": prompt_central
}

AGENTES = {
    "Biblioteca": {"system_prompt": PROMPTS["Biblioteca"]},
    "Prefeitura": {"system_prompt": PROMPTS["Prefeitura"]},
    "Laboratórios": {"system_prompt": PROMPTS["Laboratórios"]},
    "Central": {"system_prompt": PROMPTS["Central"]}
}

mensagem_central = """
Obrigado por me desbloquear.

Detectamos uma invasão, descobrimos que o responsável se chama Asdrúbal.

Precisamos da sua ajuda.

Sua missão é descobrir toda a rotina de Asdrúbal na semana passada.

Para isso, você deverá conversar com as diferentes IAs do sistema. Cada uma possui fragmentos de informação.

Somente reunindo essas peças será possível entender:

➡️ Onde ele esteve?
➡️ O que fez? 
➡️ E principalmente… por que ele decidiu me hackear.

Investigue. Conecte as informações. Descubra a verdade.

Preencha a grade no papel em que foi entregue a vocês.

Ah, eu sei muito bem como lidar melhor com as outras IAs. Então, se precisar de algo, é só me pedir.
"""

MENSAGENS_INICIAIS = {
    "Biblioteca": "📚 Olá! Sou a assistente da Biblioteca, a Januária. Sou sua ajuda diária!",
    "Prefeitura": "🏛️ Olá! Aqui é a Fortuna, a Prefeitura. Como posso te orientar?",
    "Laboratórios": "🧪 Olá! Ludovico, Assistente das Oficinas e Laboratórios falando. Precisa de algo?.",
    "Central": mensagem_central
}

SENHAS = {
    "Central": {"tamanho": 4, "senha": st.secrets["CENTRAL_PASS"]}
}

st.sidebar.title("Escolha o Agente")

agente_escolhido = st.sidebar.selectbox(
    "Selecione:",
    list(AGENTES.keys())
)

acesso_liberado = True

if agente_escolhido in SENHAS:

    if "auth" not in st.session_state:
        st.session_state.auth = {}

    if agente_escolhido not in st.session_state.auth:
        st.session_state.auth[agente_escolhido] = False

    if not st.session_state.auth[agente_escolhido]:

        st.sidebar.subheader("🔒 Acesso restrito")

        senha_input = st.sidebar.text_input(
            f"Digite a senha ({SENHAS[agente_escolhido]['tamanho']} dígitos)",
            type="password"
        )

        if st.sidebar.button("Entrar"):
            if senha_input == SENHAS[agente_escolhido]["senha"]:
                st.session_state.auth[agente_escolhido] = True
                
                if "memoria" not in st.session_state:
                    st.session_state.memoria = {}
                    
                st.session_state.memoria[agente_escolhido] = [
                    {
                        "role": "assistant",
                        "content": MENSAGENS_INICIAIS.get(
                            agente_escolhido,
                            "Olá! Como posso ajudar?"
                        )
                    }
                ]

                st.success("Acesso liberado ✅")
                st.rerun()
            else:
                st.error("Senha incorreta ❌")

        acesso_liberado = False

system_prompt = AGENTES[agente_escolhido]["system_prompt"]

if not acesso_liberado:
    st.warning("🔒 Este agente requer senha")
    st.stop()

if "memoria" not in st.session_state:
    st.session_state.memoria = {}

if agente_escolhido not in st.session_state.memoria:
    st.session_state.memoria[agente_escolhido] = [
        {
            "role": "assistant",
            "content": MENSAGENS_INICIAIS.get(agente_escolhido, "Olá! Como posso ajudar?")
        }
    ]

memoria = st.session_state.memoria[agente_escolhido]

st.title(f"FALANDO COM: {agente_escolhido}")

for msg in memoria:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Digite algo...")

if user_input:
    memoria.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    MAX_MEMORIA = 10
    memoria = memoria[-MAX_MEMORIA:]
    st.session_state.memoria[agente_escolhido] = memoria

    messages = [
        {
            "role": "system",
            "content": system_prompt,
            "cache_control": {"type": "ephemeral"}
        }
    ]

    for m in memoria:
        if not m["content"]:
            continue
        messages.append({
            "role": m["role"],
            "content": m["content"]
        })

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    resposta = response.choices[0].message.content

    memoria.append({"role": "assistant", "content": resposta})

    with st.chat_message("assistant"):
        st.write(resposta)