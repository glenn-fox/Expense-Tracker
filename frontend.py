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
    

def main():

    st.set_page_config(page_title="My Budget", layout="wide")

    st.title("My Budget")
    sync_transactions()

    initialize_session_state()

    #df = get_transactions()

    #df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce").dt.date
    accounts = get_accounts()
    categories = get_categories()
    category_map = dict(zip(categories["category_name"], categories["category_id"]))

    tab1, tab2, tab3, tab4 = st.tabs(["Transactions", "Summary", "Categories", "Import CSV"])
    with tab1:
        
        filtered_df = st.session_state.original_df.copy()

        category_list = categories["category_name"].tolist()

        category_list.insert(0, "")
        
        col1, col2, col3, col4 = st.columns(4)
        #search for descriptions
        description_search = col1.text_input(
            label="Search for transaction desctription",
            placeholder="Search",
            key="search_input"
        )

        if description_search:
            search_term = description_search.lower()

            filtered_df = filtered_df[filtered_df['description'].str.lower().str.contains(search_term, na=False)]
        #else:
            
            #filtered_df = df.copy()

        #search for transaction type
        transaction_type_search = col2.selectbox("Select Transaction Type", ("", "Income", "Expense"))

        if transaction_type_search:
            filtered_df = filtered_df[filtered_df["transaction_type_name"].str.contains(transaction_type_search)]

        #search for categories
        category_search = col3.selectbox("Select Category", category_list)

        if category_search:
            filtered_df = filtered_df[filtered_df["category_name"].str.contains(category_search, na=False)]

        date_search_start, date_search_end = col4.date_input(
            "Select Dates",
            (datetime.date(2024, 1, 1), datetime.date.today()),
            datetime.date(2024, 1, 1), datetime.date.today(),
            format="MM/DD/YYYY"
        )
        if date_search_start and date_search_end:
            filtered_df = filtered_df[filtered_df['transaction_date'].between(date_search_start, date_search_end)]

        st.session_state.edited_df = st.data_editor(
            filtered_df,
            key=f"data_editor_{st.session_state.editor_key}",
            column_order=["description", "transaction_date", "amount", "transaction_type_name", "category_name"],
            column_config={
                "description": "Description",
                "transaction_date": st.column_config.DateColumn(
                    "Transaction Date",
                    format="MM/DD/YYYY",
                ), 
                "amount": st.column_config.NumberColumn(
                    "Amount",
                    format="dollar",
                ),
                "transaction_type_name": "Transaction Type",
                "category_name": st.column_config.SelectboxColumn(
                    "Category",
                    options=category_list
                )
            },
            hide_index=True
        )


        editor_state = st.session_state.get(f"data_editor_{st.session_state.editor_key}", {})

        edited_rows = editor_state.get("edited_rows", {})

        changed_list = []
        for row_idx, changes in edited_rows.items():
            split_id = int(st.session_state.edited_df.iloc[row_idx]["split_id"])
            description = st.session_state.edited_df.iloc[row_idx]["description"]

            if "category_name" in changes:
                new_category_name = changes["category_name"]
                new_category_id = category_map[new_category_name] 

                changed_list.append({
                    "split_id": split_id,
                    "description": description,
                    "new_category_name": new_category_name,
                    "new_category_id": new_category_id
                })



        update_list = []
        changed_df = pd.DataFrame(changed_list)
        if not changed_df.empty:
            
            for i in changed_list:
                update_list.append((i["new_category_id"], int(i["split_id"])))
            
            flex = st.container(horizontal=True, horizontal_alignment="right")

            flex.button('Reset', on_click=reset_dataframe, type="primary")
            flex.button('Submit', on_click=submit_changes, args=[update_list])


            st.dataframe(changed_df,
                        column_order=["description", "new_category_name"],
                        column_config={
                         "description": "Description",
                         "new_category_name": "New Category"

                         },
                        hide_index=True)



    with tab2:
        "hello"

        category_search = st.selectbox("Select Category", category_list, key="category_summary")

        summary_df = get_monthly_category_summary()
        filtered_summary_df = summary_df

        filtered_summary_df = filtered_summary_df[filtered_summary_df["category_name"].str.contains(category_search)]

        filtered_summary_df

        fig = px.line(filtered_summary_df, x='year_month', y='total')

        st.plotly_chart(fig)


        #summary_df = month_summary()
    
        #summary_df['year_month'] = pd.to_datetime(summary_df['year_month'])

        #summary_df = summary_df.pivot_table(
        #    index='year_month',
        #    columns='transaction_type_name',
        #    values='amount'
        #).reset_index()

        #summary_df

    with tab3:
        col1, col2 = st.columns([3,1])

        col1.dataframe(categories, hide_index=True)

        new_category = col2.text_input("Enter New Category")
        new_parent_category = col2.selectbox("Enter Parent Category", category_list)
        is_visable = col2.selectbox("Should the category be visable", ["True", "False"])
        col2.button("Submit", on_click=submit_category, args=(new_category, new_parent_category, is_visable))

    with tab4:
        dataframe = None
        col1, col2 = st.columns(2)

        uploaded_file = col1.file_uploader("Choose a file", type="csv")
        
        selected_account = col2.selectbox("choose account", accounts["account_name"])
        account_id = int(accounts.loc[accounts['account_name'] == selected_account, 'account_id'].iloc[0])



        if uploaded_file is not None:
            dataframe = pd.read_csv(uploaded_file, skiprows=1)
            st.write(dataframe)
            st.button(label="Submit", key="import_csv_button", type="primary", on_click=submit_CSV_import, args=(dataframe, account_id))

        
        

if __name__ == "__main__":
    main()
