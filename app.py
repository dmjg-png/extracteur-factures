import streamlit as st
import pdfplumber
import pandas as pd
import re
import io

def extraire_donnees(texte):
    numero = re.search(
        r'(?:FACTURE\s*N°|Facture\s*(?:n°|no|num|number|№|#|N°))\s*[:\-]?\s*([A-Z0-9\-]+)',
        texte, re.IGNORECASE
    )
    date = re.search(
        r'(?:DATE|Date[^:éà]*)\s*:\s*(\d{1,2}\s*[\/\-\.]\s*\d{1,2}\s*[\/\-\.]\s*\d{2,4})',
        texte, re.IGNORECASE
    )
    if not date:
        date = re.search(r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})', texte)
    echeance = re.search(
        r'(?:ÉCHÉANCE|Échéance|Echeance|Due\s*date)\s*[:\-]?\s*([^\n]+)',
        texte, re.IGNORECASE
    )
    total_ht = re.search(
        r'(?:TOTAL\s*HT|Total\s*HT|Sous[\s\-]total|Subtotal|HT\s*total)\s*[:\-]?\s*([\d][\d\s,\.]+\s*€?)',
        texte, re.IGNORECASE
    )
    if not total_ht:
        total_ht = re.search(
            r'^Total\s*:\s*([\d][\d\s,\.]+\s*€?)',
            texte, re.IGNORECASE | re.MULTILINE
        )
    tva = re.search(
        r'TVA\s*\([^)]*\)\s*[:\-]?\s*([\d][\d\s,\.]+\s*€?)',
        texte, re.IGNORECASE
    )
    if not tva:
        tva = re.search(
            r'(?:^TVA|^T\.V\.A)\s*[:\-]?\s*([\d][\d\s,\.]+\s*€?)',
            texte, re.IGNORECASE | re.MULTILINE
        )
    if not tva:
        tva = re.search(
            r'TVA\s*[:\-]\s*([\d][\d\s,\.]+\s*€?)',
            texte, re.IGNORECASE
        )
    total_ttc = re.search(
        r'(?:TOTAL\s*TTC|Total\s*TTC|Net\s*à\s*payer|Montant\s*TTC|Amount\s*due)\s*[:\-]?\s*([\d][\d\s,\.]+\s*€?)',
        texte, re.IGNORECASE
    )
    if not total_ttc:
        total_ttc = re.search(
            r'(?:^TOTAL|^Total)\s*[:\-]?\s*([\d][\d\s,\.]+\s*€)',
            texte, re.IGNORECASE | re.MULTILINE
        )

    def get(match):
        if match:
            groups = [g for g in match.groups() if g is not None and g.strip() != '']
            if groups:
                return groups[0].strip()
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

    resultat =
