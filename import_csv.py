import streamlit as st
import pandas as pd
import datetime
from backend import *
from frontend_functions import *
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Transactions", layout="wide")

st.title("Import CSV")
sync_transactions()

initialize_session_state()


dataframe = None
col1, col2 = st.columns(2)

uploaded_file = col1.file_uploader("Choose a file", type="csv")

selected_account = col2.selectbox("choose account", st.session_state.accounts["account_name"])
account_id = int(st.session_state.accounts.loc[st.session_state.accounts['account_name'] == selected_account, 'account_id'].iloc[0])



if uploaded_file is not None:
    dataframe = pd.read_csv(uploaded_file, skiprows=1)
    st.write(dataframe)
    st.button(label="Submit", key="import_csv_button", type="primary", on_click=submit_CSV_import, args=(dataframe, account_id))
