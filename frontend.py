import streamlit as st
# from backend import *
# import plotly.graph_objects as go
# from plotly.subplots import make_subplots


def main():

    pg = st.navigation(
        [
            st.Page("transactions.py", title="Tansactions"),
            st.Page("summary.py", title="Summary"),
            st.Page("categories.py", title="Categories"),
            st.Page("import_csv.py", title="Import CSV"),
            st.Page("transaction_rules.py", title="Transaction Rules"),
        ]
    )
    pg.run()


if __name__ == "__main__":
    main()
