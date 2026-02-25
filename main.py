import streamlit as st
import google.generativeai as genai

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

with open("prompts/BIBLIOTECA.txt", "r", encoding="utf-8") as f:
    prompt_biblioteca = f.read()

with open("prompts/PREFEITURA.txt", "r", encoding="utf-8") as f:
    prompt_prefeitura = f.read()

with open("prompts/LABORATORIOS.txt", "r", encoding="utf-8") as f:
    prompt_laboratorios = f.read()

with open("prompts/CENTRAL.txt", "r", encoding="utf-8") as f:
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

MENSAGENS_INICIAIS = {
    "Biblioteca": "📚 Olá! Sou a assistente da Biblioteca. Em que posso ajudar?",
    "Prefeitura": "🏛️ Olá! Aqui é a Prefeitura. Como posso te orientar? Possuo registros de câmeras, ambulatório, calendário, restaurantes e achados e perdidos, além de outras informações sobre o CUP.",
    "Laboratórios": "🧪 Olá! Assistente dos Laboratórios falando. Precisa de algo? Possuo acesso aos registros dos laboratórios de Química, Física, Têxtil, Computação.",
    "Central": "🖥️ Olá. Você acessou a Central. Você tem acesso aqui a outras informações que as outras IAs não tem.\nSua missão é a seguinte:\n\nA organização do Intervalo Cultural da CUP identificou uma inconsistência na programação oficial do evento.\n\nUma das bandas listadas — Trombonoise — não passou pelo processo formal de inscrição.\n\nA responsável pelo evento, Fortuna, afirma que:\n\n❗ Não aprovou a banda\n❗ Não recebeu inscrição\n❗ Mas ela aparece no sistema oficial\n\nIsso indica que:\n\n👉 O sistema pode ter sido manipulado\n👉 Alguém inseriu a banda diretamente\n\nUma investigação foi iniciada.\n\nSeu objetivo é descobrir:\n\n🔎 Quem inseriu a banda Trombonoise no sistema?"}

SENHAS = {
    "Biblioteca": {"tamanho": 3, "senha": st.secrets["BIBLIOTECA_PASS"]},
    "Laboratórios": {"tamanho": 4, "senha": st.secrets["LABORATORIOS_PASS"]},
    "Central": {"tamanho": 5, "senha": st.secrets["CENTRAL_PASS"]}
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

    contexto = system_prompt + "\n\n"

    for m in memoria:
        if not m["content"]:
            continue
        if m["role"] == "user":
            contexto += f"Usuário: {m['content']}\n"
        else:
            contexto += f"Assistente: {m['content']}\n"

    response = model.generate_content(contexto)

    try:
        resposta = response.text
    except:
        if response.candidates and response.candidates[0].content.parts:
            resposta = response.candidates[0].content.parts[0].text
        else:
            resposta = None

    if resposta:
        memoria.append({"role": "assistant", "content": resposta})
    else:
        resposta = "⚠️ O agente não conseguiu responder."

    with st.chat_message("assistant"):
        st.write(resposta)