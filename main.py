import streamlit as st
import google.generativeai as genai
import os

# --- CONFIG API ---
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

model = genai.GenerativeModel("gemini-1.5-flash")

# --- LENDO OS TXT ---
with open("prompts/FORENSE.txt", "r", encoding="utf-8") as f:
    prompt_forense = f.read()

with open("prompts/CLARA.txt", "r", encoding="utf-8") as f:
    prompt_clara = f.read()

with open("prompts/DANTE.txt", "r", encoding="utf-8") as f:
    prompt_dante = f.read()

with open("prompts/JAVIER.txt", "r", encoding="utf-8") as f:
    prompt_javier = f.read()

with open("prompts/JUNIOR.txt", "r", encoding="utf-8") as f:
    prompt_junior = f.read()

with open("prompts/MARCOS.txt", "r", encoding="utf-8") as f:
    prompt_marcos = f.read()

# --- DEFINIÇÃO DOS AGENTES ---

PROMPTS = {
    "Cientista Forense": prompt_forense,

    "Clara": prompt_clara,

    "Dante": prompt_dante,

    "Javier": prompt_javier,

    "Júnior": prompt_junior,

    "Marcos": prompt_marcos
}

AGENTES = {
    "Cientista Forense": {
        "system_prompt": PROMPTS["Cientista Forense"]
    },

    "Clara": {
        "system_prompt": PROMPTS["Clara"]
    },

    "Dante": {
        "system_prompt": PROMPTS["Dante"]
    },

    "Javier": {
        "system_prompt": PROMPTS["Javier"]
    },

    "Júnior": {
        "system_prompt": PROMPTS["Júnior"]
    },

    "Marcos": {
        "system_prompt": PROMPTS["Marcos"]
    }
}

# --- SIDEBAR ---
st.sidebar.title("Escolha o Agente")

agente_escolhido = st.sidebar.selectbox(
    "Selecione:",
    list(AGENTES.keys())
)

system_prompt = AGENTES[agente_escolhido]["system_prompt"]

# --- MEMÓRIA POR AGENTE ---
if "memoria" not in st.session_state:
    st.session_state.memoria = {}

if agente_escolhido not in st.session_state.memoria:
    st.session_state.memoria[agente_escolhido] = []

memoria = st.session_state.memoria[agente_escolhido]

# --- UI ---
st.title(f"FALANDO COM: {agente_escolhido}")

for msg in memoria:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# --- INPUT ---
user_input = st.chat_input("Digite algo...")

if user_input:
    memoria.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    # Monta contexto
    contexto = system_prompt + "\n\n"

    for m in memoria:
        if m["role"] == "user":
            contexto += f"Usuário: {m['content']}\n"
        else:
            contexto += f"Assistente: {m['content']}\n"

    response = model.generate_content(contexto)

    resposta = response.text

    memoria.append({"role": "assistant", "content": resposta})

    with st.chat_message("assistant"):
        st.write(resposta)