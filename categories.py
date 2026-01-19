import streamlit as st
import pandas as pd
import datetime
from backend import *
from frontend_functions import *
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Categories", layout="wide")

st.title("Categories")
sync_transactions()

initialize_session_state()



col1, col2 = st.columns([3,1])

col1.dataframe(st.session_state.categories, hide_index=True)

new_category = col2.text_input("Enter New Category")
new_parent_category = col2.selectbox("Enter Parent Category", st.session_state.category_list)
is_visable = col2.selectbox("Should the category be visable", ["True", "False"])
col2.button("Submit", on_click=submit_category, args=(new_category, new_parent_category, is_visable))

