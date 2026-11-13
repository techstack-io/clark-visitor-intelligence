import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Clark Visitor Intelligence",
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

    # Load original dataset
    df = pd.read_excel(uploaded_file)

    st.success("File uploaded successfully.")

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
    ).copy()

    # Convert mixed-type identifier columns to strings
    for col in ["Company ID", "Visit ID", "Visitor ID (Leadfeeder)"]:
        if col in df_clean.columns:
            df_clean[col] = df_clean[col].astype("string")

    # Dataset overview
    st.subheader("Dataset Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Records", len(df_clean))
    col2.metric("Original Columns", df.shape[1])
    col3.metric("Cleaned Columns", df_clean.shape[1])

    # Display cleaned dataset
    st.subheader("Cleaned Dataset")
    st.dataframe(df_clean, width="stretch")

    # Display column names
    st.subheader("Remaining Columns")
    st.write(df_clean.columns.tolist())
