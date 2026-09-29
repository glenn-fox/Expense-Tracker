import streamlit as st

# import pandas as pd
# import datetime
from backend import (
    run_transaction_rules,
    add_transaction_rule,
    sync_transactions,
    get_transaction_rules,
)
from frontend_functions import reset_dataframe, initialize_session_state
# import plotly.express as px
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots


def submit_transaction_rule(description_search, new_category_id, transaction_type_id):
    if description_search == "" or new_category_id == "" or transaction_type_id == "":
        st.toast("Missing Data")
    else:
        st.toast(
            add_transaction_rule(
                description_search, new_category_id, transaction_type_id
            )
        )


def run_rules():
    run_transaction_rules()
    reset_dataframe()
    # transactions_df = st.session_state.original_df.copy()


st.set_page_config(page_title="Transaction Rules", layout="wide")

st.title("Transaction Rules")
sync_transactions()

initialize_session_state()

tab1, tab2 = st.tabs(["Add Rule", "View Rules"])


with tab1:
    transactions_df = st.session_state.original_df.copy()

    col1, col2, col3, col4 = st.columns(4, vertical_alignment="bottom")

    description_search = col1.text_input(
        label="Search for transaction desctription",
        placeholder="Search",
        key="auto_search",
    )

    transaction_type_list = st.session_state.transaction_types[
        "transaction_type_name"
    ].tolist()
    transaction_type_list.insert(0, "")
    transaction_type_search = col2.selectbox(
        "Select Transaction Type", transaction_type_list
    )

    new_category = col3.selectbox("Select Category", st.session_state.category_list)

    if description_search:
        search_term = description_search.lower()
        transactions_df = transactions_df[
            transactions_df["description"]
            .str.lower()
            .str.contains(search_term, na=False)
        ]

    if transaction_type_search:
        transactions_df = transactions_df[
            transactions_df["transaction_type_name"].str.contains(
                transaction_type_search, na=False
            )
        ]

    st.write("Transactions the rule will apply to:")
    st.dataframe(transactions_df)

    transaction_type_id = ""
    new_category_id = ""

    if transaction_type_search != "":
        transaction_type_id = int(
            st.session_state.transaction_types.loc[
                st.session_state.transaction_types["transaction_type_name"]
                == transaction_type_search,
                "transaction_type_id",
            ].values[0]
        )

    if new_category != "":
        new_category_id = int(
            st.session_state.categories.loc[
                st.session_state.categories["category_name"] == new_category,
                "category_id",
            ].values[0]
        )

    new_rule = [description_search, new_category_id, transaction_type_id]
    col4.button(
        "Submit new rule",
        on_click=submit_transaction_rule,
        args=(description_search, new_category_id, transaction_type_id),
    )

with tab2:
    transaction_rule_df = get_transaction_rules()
    st.button("Run rules now", on_click=run_rules)
    st.write(transaction_rule_df)
