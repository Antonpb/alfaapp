import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Underwriting Analyse", layout="wide")

st.title("📊 Underwriting Analyse App")

uploaded_file = st.file_uploader("Upload Excel-fil", type=["xlsx"])
file_type = st.selectbox("Vælg datakilde", ["-- Vælg --", "Resights (handler)", "ReData (lejeniveauer)"])

if uploaded_file and file_type != "-- Vælg --":
    df = pd.read_excel(uploaded_file)

    st.subheader("Data preview")
    st.dataframe(df.head())

    if file_type == "Resights (handler)":
        st.subheader("📈 Analyse af handler (Resights)")

        if all(col in df.columns for col in ["Areal", "Salgspris"]):
            df["Pris_pr_m2"] = df["Salgspris"] / df["Areal"]
            st.write("Gennemsnitlig pris pr. m²:", round(df["Pris_pr_m2"].mean(), 2))

            fig, ax = plt.subplots()
            sns.scatterplot(data=df, x="Areal", y="Pris_pr_m2", ax=ax)
            ax.set_title("Pris pr. m² vs. Areal")
            st.pyplot(fig)
        else:
            st.error("Kolonnerne 'Areal' og 'Salgspris' mangler i data.")

    elif file_type == "ReData (lejeniveauer)":
        st.subheader("📊 Analyse af lejeniveauer (ReData)")

        if "Leje_m2" in df.columns:
            st.write("Gennemsnitlig leje pr. m²:", round(df["Leje_m2"].mean(), 2))

            fig, ax = plt.subplots()
            sns.histplot(df["Leje_m2"], bins=20, kde=True, ax=ax)
            ax.set_title("Fordeling af lejeniveauer (kr./m²)")
            st.pyplot(fig)
        else:
            st.error("Kolonnen 'Leje_m2' mangler i data.")
