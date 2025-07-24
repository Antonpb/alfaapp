import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import folium
from folium.plugins import MarkerCluster
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import os
from datetime import datetime

st.set_page_config(page_title="Underwriting Analyse", layout="wide")
st.title("📊 Underwriting Analyse App")

# Funktion til scatterplot m. trendlinje
def make_scatter_with_trend(df, x, y, title):
    fig, ax = plt.subplots(figsize=(8, 4))
    sns.regplot(data=df, x=x, y=y, ax=ax, scatter_kws={"s": 30}, line_kws={"color": "red"})
    ax.set_title(title)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    return fig

# Funktion til kort fra lat/lng
def make_map(df, lat_col="Lat", lng_col="Lng"):
    df = df.dropna(subset=[lat_col, lng_col])
    if df.empty:
        return None

    m = folium.Map(location=[df[lat_col].mean(), df[lng_col].mean()], zoom_start=13)
    marker_cluster = MarkerCluster().add_to(m)

    for _, row in df.iterrows():
        folium.Marker(location=[row[lat_col], row[lng_col]]).add_to(marker_cluster)

    map_path = "/mnt/data/map.html"
    m.save(map_path)
    return map_path

# Funktion til kort fra centroid (resights)
def parse_centroid(centroid_str):
    try:
        coords = centroid_str.replace("POINT (", "").replace(")", "").split()
        lon, lat = map(float, coords)
        return lat, lon
    except:
        return None, None

# Funktion til PDF-rapport
def make_pdf_report(title, plot_buf, map_note=""):
    pdf_path = "/mnt/data/rapport.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(title, styles["Title"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("Dato: " + datetime.now().strftime("%d-%m-%Y"), styles["Normal"]))
    elements.append(Spacer(1, 0.4 * inch))

    elements.append(Paragraph("📈 Scatterplot med trendlinje", styles["Heading2"]))
    img_path = "/mnt/data/scatter_temp.png"
    with open(img_path, "wb") as f:
        f.write(plot_buf.getvalue())
    elements.append(RLImage(img_path, width=6 * inch, height=3 * inch))
    elements.append(Spacer(1, 0.2 * inch))

    if map_note:
        elements.append(Paragraph("🗺️ Kort:", styles["Heading2"]))
        elements.append(Paragraph(map_note, styles["Normal"]))

    doc.build(elements)
    return pdf_path

# App-start
uploaded_file = st.file_uploader("Upload Excel-fil", type=["xlsx"])
file_type = st.selectbox("Vælg datakilde", ["-- Vælg --", "Resights (handler)", "ReData (lejeniveauer)"])

if uploaded_file and file_type != "-- Vælg --":
    df = pd.read_excel(uploaded_file)
    st.subheader("🔍 Data preview")
    st.dataframe(df.head())

    pdf_btn = False
    scatter_buf = io.BytesIO()
    map_path = None
    map_note = ""

    if file_type == "ReData (lejeniveauer)":
        st.subheader("📊 Analyse af lejeniveauer (ReData)")
        if all(col in df.columns for col in ["Areal", "Leje/m2"]):
            st.write("Gennemsnitlig leje pr. m²:", round(df["Leje/m2"].mean(), 2))
            fig = make_scatter_with_trend(df, "Areal", "Leje/m2", "Leje pr. m² vs. Areal")
            st.pyplot(fig)

            fig.savefig(scatter_buf, format="png")
            pdf_btn = True

            # Kort
            if all(col in df.columns for col in ["Lat", "Lng"]):
                map_path = make_map(df)
                if map_path:
                    map_note = "Kortet er genereret fra 'Lat' og 'Lng' og gemt som HTML."

        else:
            st.error("Kolonnerne 'Areal' og 'Leje/m2' mangler i data.")

    elif file_type == "Resights (handler)":
        st.subheader("📈 Analyse af handler (Resights)")
        if all(col in df.columns for col in ["Handelsdato", "Pris pr. m2 (enhedsareal)"]):
            df["Handelsdato"] = pd.to_datetime(df["Handelsdato"], errors='coerce')
            df = df.dropna(subset=["Handelsdato", "Pris pr. m2 (enhedsareal)"])
            st.write("Gennemsnitlig pris pr. m²:", round(df["Pris pr. m2 (enhedsareal)"].mean(), 2))
            fig = make_scatter_with_trend(df, "Handelsdato", "Pris pr. m2 (enhedsareal)", "Pris pr. m² over tid")
            st.pyplot(fig)

            fig.savefig(scatter_buf, format="png")
            pdf_btn = True

            # Parse centroid → lat/lng
            if "Centroid" in df.columns:
                df["Lat"], df["Lng"] = zip(*df["Centroid"].map(parse_centroid))
                map_path = make_map(df)
                if map_path:
                    map_note = "Kortet er genereret ud fra 'Centroid' koordinater og gemt som HTML."
        else:
            st.error("Kolonnerne 'Handelsdato' og 'Pris pr. m2 (enhedsareal)' mangler i data.")

    # Download PDF-knap
    if pdf_btn:
        st.subheader("📄 Download rapport")
        title = st.text_input("Titel til rapport:")
        if title:
            pdf_file = make_pdf_report(title, scatter_buf, map_note)
            with open(pdf_file, "rb") as f:
                st.download_button(
                    label="📥 Download PDF-rapport",
                    data=f,
                    file_name="rapport.pdf",
                    mime="application/pdf"
                )

