import streamlit as st
import pdfplumber
import pandas as pd
import re
import io

def extraire_donnees(texte):
    numero = re.search(r'Facture\s*[№#N°]*\s*(\d+)', texte)
    date = re.search(r'Date de facturation[:\s]+(\d{2}/\d{2}/\d{4})', texte)
    total_ttc = re.search(r'Total TTC[:\s]+([\d,\.]+)', texte)
    tva = re.search(r'TVA\([^)]+\)[:\s]+([\d,\.]+)', texte)
    return {
        "Numéro facture": numero.group(1) if numero else "Non trouvé",
        "Date": date.group(1) if date else "Non trouvé",
        "Total TTC": total_ttc.group(1) if total_ttc else "Non trouvé",
        "TVA": tva.group(1) if tva else "Non trouvé",
    }

st.title("Extracteur de factures PDF")
st.write("Uploadez une facture PDF et obtenez vos données en Excel automatiquement")

fichier = st.file_uploader("Choisir un PDF", type="pdf")

if fichier:
    with pdfplumber.open(fichier) as pdf:
        texte = ""
        for page in pdf.pages:
            texte += page.extract_text()
    
    resultat = extraire_donnees(texte)
    df = pd.DataFrame([resultat])
    
    st.success("Données extraites avec succès !")
    st.dataframe(df)
    
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    
    st.download_button(
        "Télécharger Excel",
        buffer,
        "facture.xlsx",
        "application/vnd.ms-excel" )
  
