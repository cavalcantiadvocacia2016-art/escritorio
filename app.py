import streamlit as st
import pandas as pd
import os
from cryptography.fernet import Fernet
from io import BytesIO

# ENCRYPTION_KEY = st.secrets.get("ENCRYPTION_KEY") 
ENCRYPTION_KEY = "0e_CthdxXlLTgOdwwKseCq5VlbKiHMB1Xv-Iv9GNUck=" 
st.set_page_config(page_title="Visualizador Linha a Linha", layout="centered")

# --- Inicialização de estado da sessão ---
if "started" not in st.session_state:
    st.session_state.started = False
if "idx" not in st.session_state:
    st.session_state.idx = 0
if "df" not in st.session_state:
    st.session_state.df = None

# --- Funções de navegação (circular) ---
def go_right():
    n = len(st.session_state.df)
    if n > 0:
        st.session_state.idx = (st.session_state.idx + 1) % n

def go_left():
    n = len(st.session_state.df)
    if n > 0:
        st.session_state.idx = (st.session_state.idx - 1) % n

# --- Página introdutória ---
if not st.session_state.started:
    st.markdown("<h1 style='text-align:center'>Olá, Dr. Bruno!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center'>Envie a chave e clique em <strong>Iniciar</strong>.</p>", unsafe_allow_html=True)

    uploaded = st.file_uploader("📤 Enviar chave", type=["enc"])

    if uploaded:
        try:
            encrypted_data = uploaded.read()

            # Descriptografar
            f = Fernet(ENCRYPTION_KEY.encode())
            decrypted_bytes = f.decrypt(encrypted_data)

            # Ler Excel da memória
            st.session_state.df = pd.read_excel(BytesIO(decrypted_bytes))

            st.success("Chave válida! Planilha carregada com sucesso.")

        except Exception as e:
            st.error(f"Erro ao descriptografar ou ler o arquivo: {e}")

    if st.button("Iniciar", use_container_width=True):
        if st.session_state.df is None:
            st.error("Envie uma chave válida antes de iniciar.")
            st.stop()
        st.session_state.started = True

    st.stop()

# --- Interface principal ---
df = st.session_state.df

if df is None or df.shape[0] == 0:
    st.error("Erro: planilha não carregada ou vazia.")
    st.stop()

col_l, col_c, col_r = st.columns([1,6,1])
with col_l:
    if st.button("", shortcut="left"):
        go_left()
with col_c:
    st.markdown("<h3 style='text-align:center'>Clientes</h3>", unsafe_allow_html=True)
with col_r:
    if st.button("", shortcut="right"):
        go_right()

# Índice atual
current_idx = st.session_state.idx
total = len(df)
display_idx = current_idx + 1

st.markdown(
    f"<p style='text-align:center'><strong>Atual:</strong> {display_idx} | <strong>Total:</strong> {total}</p>",
    unsafe_allow_html=True
)

# Ordem dos campos
campos = [
    ("Índice", None),
    ("Processo", "Processo"),
    ("Nome", "Nome"),
    ("Documento", "Documento"),
    ("Pena Total", "Pena Total"),
    ("Cumprida", "Cumprida"),
    ("Remanescente", "Remanescente"),
    ("Percentil", "Percentil"),
    ("Guias", "Guias"),
    ("Triagem", "Triagem"),
    ("Advogado", "Advogado"),
    ("Contato", "Contato"),
]

row = df.iloc[current_idx]

for label, colname in campos:
    value = display_idx if colname is None else row.get(colname, "")
    a, b = st.columns([2,6])
    with a:
        st.markdown(f"**{label} :**")
    with b:
        st.code(f"{value}")

st.write("---")
st.caption("Use as setas acima para navegar. A navegação é circular.")
