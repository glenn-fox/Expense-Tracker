import streamlit as st
import pandas as pd
import datetime
from backend import *
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def main():

    pg = st.navigation(["transactions.py", "summary.py", "categories.py", "import_csv.py"])
    pg.run()

        
        

if __name__ == "__main__":
    main()
