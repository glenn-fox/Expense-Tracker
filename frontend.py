import streamlit as st
import pandas as pd
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

def reset_dataframe():
    st.session_state.current_df = st.session_state.original_df.copy()
    st.session_state.editor_key += 1
    st.toast("Successfully reset category edits!")



def main():

    st.set_page_config(page_title="My Budget", layout="wide")

    initialize_session_state()

    #df = get_transactions()

    #df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce").dt.date

    categories = get_categories()
    category_map = dict(zip(categories["category_name"], categories["category_id"]))

    tab1, tab2 = st.tabs(["Transactions", "Summary"])
    with tab1:
        st.title("My Budget")
        

        my_list = categories["category_name"].tolist()

        my_list.insert(0, "")
        #print(my_list)
        
        col1, col2, col3 = st.columns(3)
        #search for descriptions
        description_search = col1.text_input(
            label="Search for transaction desctription",
            placeholder="Search",
            key="search_input"
        )

        if description_search:
            search_term = description_search.lower()

            st.session_state.current_df = st.session_state.current_df[st.session_state.current_df['description'].str.lower().str.contains(search_term, na=False)]
        #else:
            
            #filtered_df = df.copy()

        #search for transaction type
        transaction_type_search = col2.selectbox("Select Transaction Type", ("", "Income", "Expense"))

        if transaction_type_search:
            st.session_state.current_df = st.session_state.current_df[st.session_state.current_df["transaction_type_name"].str.contains(transaction_type_search)]

        #search for categories
        category_search = col3.selectbox("Select Category", my_list)

        if category_search:
            st.session_state.current_df = st.session_state.current_df[st.session_state.current_df["category_name"].str.contains(category_search)]

        edited_df = st.data_editor(
            st.session_state.current_df,
            #key="editor",
            key=f"data_editor_{st.session_state.editor_key}",
            column_order=["description", "transaction_date", "amount", "transaction_type_name", "category_name"],
            column_config={
                "description": "Description",
                "transaction_date": st.column_config.DateColumn(
                    "Transaction Date",
                    format="MM/DD/YYY",
                ), 
                "category_name": st.column_config.SelectboxColumn(
                    "Category",
                    options=my_list
                )
            },
            hide_index=True
        )

        if not edited_df.equals(st.session_state.current_df):
            st.session_state.current_df = edited_df

        editor_state = st.session_state.get(f"data_editor_{st.session_state.editor_key}", {})

        edited_rows = editor_state.get("edited_rows", {})

        changed_list = []
        for row_idx, changes in edited_rows.items():
            split_id = st.session_state.original_df.loc[row_idx, "split_id"]
            description = st.session_state.original_df.loc[row_idx, "description"]

            if "category_name" in changes:
                new_category_name = changes["category_name"]
                new_category_id = category_map[new_category_name] 

                changed_list.append({
                    "split_id": split_id,
                    "description": description,
                    "new_category_name": new_category_name,
                    "new_category_id": new_category_id
                })

        changed_df = pd.DataFrame(changed_list)
        if not changed_df.empty:
            
            st.button('Reset', on_click=reset_dataframe)


            st.dataframe(changed_df,
                        column_order=["description", "new_category_name"],
                        hide_index=True)


    with tab2:
        "hello"
        summary_df = month_summary()
    
        summary_df['year_month'] = pd.to_datetime(summary_df['year_month'])

        summary_df = summary_df.pivot_table(
            index='year_month',
            columns='transaction_type_name',
            values='amount'
        ).reset_index()

        summary_df

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Scatter(
                x=summary_df['year_month'],
                y=summary_df['Income'],
                name='Income',
                mode='lines+markers',
                line=dict(color='green')
            ),
            secondary_y=False,
        )
        # 3. Add Expense trace (Secondary Y-axis)
        fig.add_trace(
            go.Scatter(
                x=summary_df['year_month'], 
                y=summary_df['Expense'], 
                name='Expense', 
                mode='lines+markers', 
                line=dict(color='red')
            ),
            secondary_y=True, # Use the secondary Y-axis
        )

        # 4. Customize the layout
        fig.update_layout(
            title_text="Monthly Income vs. Expense",
            xaxis_title="Month/Year",
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        # 5. Set y-axes titles and colors to match the traces
        fig.update_yaxes(title_text="<b>Income</b> Amount", secondary_y=False, color="green")
        fig.update_yaxes(title_text="<b>Expense</b> Amount", secondary_y=True, color="red")

        fig


if __name__ == "__main__":
    main()
