import os
import sys
import streamlit as st
from sqlalchemy.orm import Session

# Ensure project root is on sys.path so 'src' imports work when running via Streamlit
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
	sys.path.append(PROJECT_ROOT)

from src.database import SessionLocal
from src.chat.flows import CustomerFlow, SupplierFlow


def get_session() -> Session:
	if "db" not in st.session_state:
		st.session_state.db = SessionLocal()
	return st.session_state.db


def get_flow(user_type: str):
	db = get_session()
	key = f"flow_{user_type}"
	if key not in st.session_state:
		st.session_state[key] = CustomerFlow(db) if user_type == "customer" else SupplierFlow(db)
	return st.session_state[key]


st.set_page_config(page_title="KcartBot", page_icon="🤖", layout="centered")
st.title("KcartBot - Agri-Commerce Assistant")

user_type = st.radio("Choose mode:", ["customer", "supplier"], horizontal=True, index=0)
flow = get_flow(user_type)

if "messages" not in st.session_state:
	st.session_state.messages = []

for role, content in st.session_state.messages:
	with st.chat_message(role):
		st.markdown(content)

prompt = st.chat_input("Type your message...")
if prompt:
	st.session_state.messages.append(("user", prompt))
	with st.chat_message("user"):
		st.markdown(prompt)

	try:
		if user_type == "customer" and "deliver" in prompt.lower() and hasattr(flow, "complete_order"):
			response = flow.complete_order("2024-12-25", "Addis Ababa")
		else:
			response = flow.handle_message(prompt)
	except Exception as e:
		response = f"I encountered an error. Please try again. Error: {str(e)}"

	st.session_state.messages.append(("assistant", response))
	with st.chat_message("assistant"):
		st.markdown(response)


