import streamlit as st
from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def carregar(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

PROMPTS = {

    # JANUÁRIA
    "januaria_26_1a": carregar("prompts26_1/a_BIBLIOTECA.txt"),
    "januaria_26_1a2": carregar("prompts26_1/a2_BIBLIOTECA.txt"),
    "januaria_26_1b": carregar("prompts26_1/b_BIBLIOTECA.txt"),
    "januaria_26_1c": carregar("prompts26_1/c_BIBLIOTECA.txt"),
    "januaria_26_2a": carregar("prompts26_2/a_BIBLIOTECA.txt"),
    "januaria_26_2b": carregar("prompts26_2/b_BIBLIOTECA.txt"),
    "januaria_26_2c": carregar("prompts26_2/c_BIBLIOTECA.txt"),
    "januaria_26_2d": carregar("prompts26_2/d_BIBLIOTECA.txt"),
    "januaria_26_2e": carregar("prompts26_2/e_BIBLIOTECA.txt"),
    "januaria_26_2f": carregar("prompts26_2/f_BIBLIOTECA.txt"),

    # FORTUNA
    "fortuna_26_1a": carregar("prompts26_1/a_PREFEITURA.txt"),
    "fortuna_26_1a2": carregar("prompts26_1/a2_PREFEITURA.txt"),
    "fortuna_26_1b": carregar("prompts26_1/b_PREFEITURA.txt"),
    "fortuna_26_1c": carregar("prompts26_1/c_PREFEITURA.txt"),
    "fortuna_26_2a": carregar("prompts26_2/a_PREFEITURA.txt"),
    "fortuna_26_2b": carregar("prompts26_2/b_PREFEITURA.txt"),
    "fortuna_26_2c": carregar("prompts26_2/c_PREFEITURA.txt"),
    "fortuna_26_2d": carregar("prompts26_2/d_PREFEITURA.txt"),
    "fortuna_26_2e": carregar("prompts26_2/e_PREFEITURA.txt"),
    "fortuna_26_2f": carregar("prompts26_2/f_PREFEITURA.txt"),

    # LUDOVICO
    "ludovico_26_1a": carregar("prompts26_1/a_LABORATORIOS.txt"),
    "ludovico_26_1a2": carregar("prompts26_1/a2_LABORATORIOS.txt"),
    "ludovico_26_1b": carregar("prompts26_1/b_LABORATORIOS.txt"),
    "ludovico_26_1c": carregar("prompts26_1/c_LABORATORIOS.txt"),
    "ludovico_26_2a": carregar("prompts26_2/a_LABORATORIOS.txt"),
    "ludovico_26_2b": carregar("prompts26_2/b_LABORATORIOS.txt"),
    "ludovico_26_2c": carregar("prompts26_2/c_LABORATORIOS.txt"),
    "ludovico_26_2d": carregar("prompts26_2/d_LABORATORIOS.txt"),
    "ludovico_26_2e": carregar("prompts26_2/e_LABORATORIOS.txt"),
    "ludovico_26_2f": carregar("prompts26_2/f_LABORATORIOS.txt"),

    # CENTRAL
    "central_26_1a": carregar("prompts26_1/a_CENTRAL.txt"),
    "central_26_1a2": carregar("prompts26_1/a2_CENTRAL.txt"),
    "central_26_1b": carregar("prompts26_1/b_CENTRAL.txt"),
    "central_26_1c": carregar("prompts26_1/c_CENTRAL.txt"),
    "central_26_2a": carregar("prompts26_2/a_CENTRAL.txt"),
    "central_26_2b": carregar("prompts26_2/b_CENTRAL.txt"),
    "central_26_2c": carregar("prompts26_2/c_CENTRAL.txt"),
    "central_26_2d": carregar("prompts26_2/d_CENTRAL.txt"),
    "central_26_2e": carregar("prompts26_2/e_CENTRAL.txt"),
    "central_26_2f": carregar("prompts26_2/f_CENTRAL.txt"),
}

MENSAGENS_INICIAIS = {
    "januaria": "📚 Olá! Sou a assistente da Biblioteca, a Januária. Sou sua ajuda diária!",
    "fortuna": "🏛️ Olá! Aqui é a Fortuna, a Prefeitura. Como posso te orientar?",
    "ludovico": "🧪 Olá! Ludovico, Assistente das Oficinas e Laboratórios falando. Precisa de algo?.",
}

CENTRAIS = [
    "central_26_1a", "central_26_1a2", "central_26_1b", "central_26_1c",
    "central_26_2a", "central_26_2b", "central_26_2c", "central_26_2d", "central_26_2e", "central_26_2f",
]

# -------------------------------
# DETECTAR ROTA
# -------------------------------

query = st.query_params
rota = query.get("agente", "").lower()

try:
    personagem, versao = rota.split("_", 1)
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

        mensagem_central = f"""
        MENSAGEM DA CUPULA!!!!!!!!!!
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
