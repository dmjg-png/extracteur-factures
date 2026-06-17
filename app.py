import streamlit as st
import pdfplumber
import pandas as pd
import re
import io

def extraire_donnees(texte):
    numero = re.search(
        r'(?:Facture|Invoice|FACTURE)\s*(?:n°|no|num|number|№|#)\s*:?\s*([A-Z0-9\-]+)',
        texte, re.IGNORECASE
    )
    date = re.search(
        r'(?:Date[^:]*:\s*)(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
        texte, re.IGNORECASE
    )
    if not date:
        date = re.search(r'(\d{2}\/\d{2}\/\d{2,4})', texte)
    total_ttc = re.search(
        r'(?:Total\s*TTC|Net\s*à\s*payer)[^\d]*([\d\s,\.]+\s*€?)',
        texte, re.IGNORECASE
    )
    if not total_ttc:
        total_ttc = re.search(
            r'(?:^TOTAL|^Total)[^\d]*([\d\s,\.]+\s*€)',
            texte, re.IGNORECASE | re.MULTILINE
        )
    tva = re.search(
        r'TVA[^:]*:\s*([\d\s,\.]+\s*€?)',
        texte, re.IGNORECASE
    )
    total_ht = re.search(
        r'(?:Total\s*HT|Sous[\s\-]total|Subtotal)[^\d]*([\d\s,\.]+\s*€?)',
        texte, re.IGNORECASE
    )
    if not total_ht:
        total_ht = re.search(
            r'^Total:\s*([\d\s,\.]+\s*€?)',
            texte, re.IGNORECASE | re.MULTILINE
        )
    echeance = re.search(
        r'(?:Échéance|Echeance|Due\s*date)[^\d]*(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})',
        texte, re.IGNORECASE
    )

    def get(match):
        if match:
            for g in match.groups():
                if g:
                    return g.strip()
        return "Non trouvé"

    return {
        "Numéro facture": get(numero),
        "Date": get(date),
        "Échéance": get(echeance),
        "Total HT": get(total_ht),
        "TVA": get(tva),
        "Total TTC": get(total_ttc),
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
        "application/vnd.ms-excel"
    )
