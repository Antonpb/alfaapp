import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

st.set_page_config(page_title="Underwriting Analyse", layout="wide")
st.title("📊 Underwriting Analyse App")

uploaded_file = st.file_uploader("Upload Excel-fil", type=["xlsx"])
file_type = st.selectbox("Vælg datakilde", ["-- Vælg --", "Resights (handler)", "ReData (lejeniveauer)"])

if uploaded_file and file_type != "-- Vælg --":
    df = pd.read_excel(uploaded_file)

    st.subheader("🔍 Data preview")
    st.dataframe(df.head())

    if file_type == "ReData (lejeniveauer)":
        st.subheader("📊 Analyse af lejeniveauer (ReData)")

        if all(col in df.columns for col in ["Areal", "Leje/m2"]):
            st.write("Gennemsnitlig leje pr. m²:", round(df["Leje/m2"].mean(), 2))

            fig, ax = plt.subplots(figsize=(8, 4))
            sns.scatterplot(data=df, x="Areal", y="Leje/m2", ax=ax)
            ax.set_title("Leje pr. m² vs. Areal")
            ax.set_xlabel("Areal (m²)")
            ax.set_ylabel("Leje pr. m² (kr.)")
            st.pyplot(fig)

            # Gem figuren til download
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            st.download_button(
                label="📥 Download scatterplot",
                data=buf.getvalue(),
                file_name="scatterplot_redata.png",
                mime="image/png"
            )
        else:
            st.error("Kolonnerne 'Areal' og 'Leje/m2' mangler i data.")

    elif file_type == "Resights (handler)":
        st.subheader("📈 Analyse af handler (Resights)")

        if all(col in df.columns for col in ["Handelsdato", "Pris pr. m2 (enhedsareal)"]):
            df["Handelsdato"] = pd.to_datetime(df["Handelsdato"], errors='coerce')
            df = df.dropna(subset=["Handelsdato", "Pris pr. m2 (enhedsareal)"])

            st.write("Gennemsnitlig pris pr. m²:", round(df["Pris pr. m2 (enhedsareal)"].mean(), 2))

            fig, ax = plt.subplots(figsize=(8, 4))
            sns.scatterplot(data=df, x="Handelsdato", y="Pris pr. m2 (enhedsareal)", ax=ax)
            ax.set_title("Pris pr. m² over tid")
            ax.set_xlabel("Handelsdato")
            ax.set_ylabel("Pris pr. m² (kr.)")
            st.pyplot(fig)

            # Gem figuren til download
            buf = io.BytesIO()
            fig.savefig(buf, format="png")
            st.download_button(
                label="📥 Download scatterplot",
                data=buf.getvalue(),
                file_name="scatterplot_resights.png",
                mime="image/png"
            )
        else:
            st.error("Kolonnerne 'Handelsdato' og 'Pris pr. m2 (enhedsareal)' mangler i data.")
