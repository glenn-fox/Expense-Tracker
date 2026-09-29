import streamlit as st

# import pandas as pd
# import datetime
from backend import sync_transactions, get_monthly_category_summary
from frontend_functions import initialize_session_state
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="Summary", layout="wide")

st.title("Summary")
sync_transactions()

initialize_session_state()


category_search = st.selectbox(
    "Select Category", st.session_state.category_list, key="category_summary"
)

summary_df = get_monthly_category_summary()
filtered_summary_df = summary_df

filtered_summary_df = filtered_summary_df[
    filtered_summary_df["category_name"].str.contains(category_search)
]


fig = px.line(filtered_summary_df, x="year_month", y="total")

st.plotly_chart(fig)


# summary_df = month_summary()

# summary_df['year_month'] = pd.to_datetime(summary_df['year_month'])

# summary_df = summary_df.pivot_table(
#    index='year_month',
#    columns='transaction_type_name',
#    values='amount'
# ).reset_index()

# summary_df
