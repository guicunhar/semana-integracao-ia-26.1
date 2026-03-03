import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def carregar(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

PROMPTS = {

    # JANUÁRIA
    "januaria_a": carregar("prompts/a_BIBLIOTECA.txt"),
    "januaria_a2": carregar("prompts/a2_BIBLIOTECA.txt"),
    "januaria_b": carregar("prompts/b_BIBLIOTECA.txt"),
    "januaria_c": carregar("prompts/c_BIBLIOTECA.txt"),

    # FORTUNA
    "fortuna_a": carregar("prompts/a_PREFEITURA.txt"),
    "fortuna_a2": carregar("prompts/a2_PREFEITURA.txt"),
    "fortuna_b": carregar("prompts/b_PREFEITURA.txt"),
    "fortuna_c": carregar("prompts/c_PREFEITURA.txt"),

    # LUDOVICO
    "ludovico_a": carregar("prompts/a_LABORATORIOS.txt"),
    "ludovico_a2": carregar("prompts/a2_LABORATORIOS.txt"),
    "ludovico_b": carregar("prompts/b_LABORATORIOS.txt"),
    "ludovico_c": carregar("prompts/c_LABORATORIOS.txt"),

    # CENTRAL
    "central_a": carregar("prompts/a_CENTRAL.txt"),
    "central_a2": carregar("prompts/a2_CENTRAL.txt"),
    "central_b": carregar("prompts/b_CENTRAL.txt"),
    "central_c": carregar("prompts/c_CENTRAL.txt"),
}

PERSONA = {
    "a": "Asdrúbal",
    "a2": "Asdrúbal",
    "b": "Roberval",
    "c": "Cíntia"
}

MENSAGENS_INICIAIS = {
    "januaria": "📚 Olá! Sou a assistente da Biblioteca, a Januária. Sou sua ajuda diária!",
    "fortuna": "🏛️ Olá! Aqui é a Fortuna, a Prefeitura. Como posso te orientar?",
    "ludovico": "🧪 Olá! Ludovico, Assistente das Oficinas e Laboratórios falando. Precisa de algo?.",
}

CENTRAIS = ["central_a", "central_a2", "central_b", "central_c"]

# -------------------------------
# DETECTAR ROTA
# -------------------------------

query = st.query_params
rota = query.get("agente", "").lower()

try:
    personagem, versao = rota.split("_")
except:
    st.error("Rota inválida.")
    st.stop()

if rota not in PROMPTS:
    st.error("Agente não existe.")
    st.stop()

system_prompt = PROMPTS[rota]

# -------------------------------
# SENHA CENTRAL
# -------------------------------

acesso_liberado = True

if rota in CENTRAIS:

    if "auth" not in st.session_state:
        st.session_state.auth = {}

    if rota not in st.session_state.auth:
        st.session_state.auth[rota] = False

    if not st.session_state.auth[rota]:

        st.subheader("🔒 Acesso restrito")

        senha_input = st.text_input("Digite a senha", type="password")

        if st.button("Entrar"):
            if senha_input == st.secrets["CENTRAL_PASS"]:
                st.session_state.auth[rota] = True
                st.success("Acesso liberado ✅")
                st.rerun()
            else:
                st.error("Senha incorreta ❌")

        acesso_liberado = False

if not acesso_liberado:
    st.stop()

# -------------------------------
# MEMÓRIA
# -------------------------------

if "memoria" not in st.session_state:
    st.session_state.memoria = {}

if rota not in st.session_state.memoria:

    if personagem == "central":

        nome_persona = PERSONA.get(versao, "Desconhecido")

        mensagem_central = f"""
Obrigado por me desbloquear.

Detectamos uma invasão, descobrimos que o responsável se chama {nome_persona}.

Precisamos da sua ajuda.

Sua missão é descobrir toda a rotina dele na semana passada.

Para isso, você deverá conversar com as diferentes IAs do sistema. Cada uma possui fragmentos de informação.

Somente reunindo essas peças será possível entender:

➡️ Onde ele esteve?
➡️ O que fez?
➡️ E principalmente… por que ele decidiu me hackear.

Investigue. Conecte as informações. Descubra a verdade.

Preencha a grade no papel em que foi entregue a vocês.

Ah, eu sei muito bem como lidar melhor com as outras IAs. Então, se precisar de algo, é só me pedir.
"""

        st.session_state.memoria[rota] = [
            {"role": "assistant", "content": mensagem_central}
        ]

    else:

        st.session_state.memoria[rota] = [
            {
                "role": "assistant",
                "content": MENSAGENS_INICIAIS.get(
                    personagem,
                    "Olá! Como posso ajudar?"
                )
            }
        ]

memoria = st.session_state.memoria[rota]

# -------------------------------
# INTERFACE
# -------------------------------

st.title(f"FALANDO COM: {personagem.upper()}")

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
    st.session_state.memoria[rota] = memoria

    messages = [
        {
            "role": "system",
            "content": system_prompt
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
