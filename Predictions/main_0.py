import pandas as pd
import streamlit as st


st.set_page_config(layout="wide")


path_excel_predictions = r"C:\Users\abrig\Documents\Coding_Practice\Python\Jerseys\NHLGamePredictions_2526_copy.xlsx"


@st.cache_data(ttl=60*60, show_spinner=True, show_time=True)
def load_excel_predictions() -> pd.DataFrame:
    """Load predictions excel"""
    # Sheet name correspondes to last year, data is from this season
    df = pd.read_excel(path_excel_predictions, sheet_name="DataRegularSeason20242025", skiprows=1)
    columns = df.columns
    cols_to_drop = [col for col in columns if str(col).lower().startswith("unnamed: ") or str(col).lower().startswith("column")]
    df = df.drop(columns=cols_to_drop)
    return df


df_predictions: pd.DataFrame = load_excel_predictions()
st.write(df_predictions.columns.tolist())

st.write(df_predictions.head(10))
st.write(df_predictions.iloc[0])
