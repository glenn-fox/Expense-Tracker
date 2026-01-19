import streamlit as st
import pandas as pd
import datetime
from backend import *
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots



def initialize_session_state():
    if 'original_df' not in st.session_state:
        st.session_state.original_df = get_transactions()
        st.session_state.original_df["transaction_date"] = pd.to_datetime(st.session_state.original_df["transaction_date"], errors="coerce").dt.date

    if 'current_df' not in st.session_state:
        st.session_state.current_df = st.session_state.original_df.copy()

    if 'editor_key' not in st.session_state:
        st.session_state.editor_key = 0

    if 'edited_df' not in st.session_state:
        st.session_state.edited_df = pd.DataFrame()

    if 'categories' not in st.session_state:
        st.session_state.categories = get_categories()

    if 'category_list' not in st.session_state:
        st.session_state.category_list = st.session_state.categories["category_name"].tolist()
        st.session_state.category_list.insert(0, "")

    if 'accounts' not in st.session_state:
        st.session_state.accounts = get_accounts()

def reset_dataframe():
    st.session_state.current_df = st.session_state.original_df.copy()
    st.session_state.editor_key += 1
    st.toast("Successfully reset category edits!")


def submit_changes(changed_list):
    st.toast(update_categories(changed_list))
    del st.session_state.original_df
    del st.session_state.current_df
    del st.session_state.editor_key
    del st.session_state.edited_df

def submit_category(category_name, parent_category, is_visable):
    if parent_category == "":
        parent_category = None 
    st.toast(add_category(category_name, parent_category, is_visable))

def submit_CSV_import(df, account_id):
    st.toast(import_file_to_db(df, account_id))

