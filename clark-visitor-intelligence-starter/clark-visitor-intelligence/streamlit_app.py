import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Clark Visitor Intelligence",
    page_icon="📊",
    layout="wide"
)

st.title("Clark Visitor Intelligence")
st.caption("Machine Learning & Website Visitor Analytics")

st.header("Leadfeeder Data Upload")

uploaded_file = st.file_uploader(
    "Upload a Leadfeeder Excel export",
    type=["xlsx"]
)

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

# Remove unnecessary columns
columns_to_drop = [
    "Company Legal Name",
    "Employees Range",
    "ICP segments",
    "Visitor email",
    "Visitor name",
    "Visitor ID (Google Analytics)",
    "Ad Content (utm_content)"
]

df_clean = df.drop(
    columns=columns_to_drop,
    errors="ignore"
)

    st.success("File uploaded successfully.")

    st.subheader("Dataset Overview")
    st.write(f"Rows: {df.shape[0]}")
    st.write(f"Columns: {df.shape[1]}")

    st.dataframe(df, use_container_width=True)

    st.subheader("Column Names")
    st.write(df.columns.tolist())
