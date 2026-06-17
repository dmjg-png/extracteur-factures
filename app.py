import streamlit as st
import pdfplumber
import pandas as pd
import anthropic
import io
import json
import re

def extraire_avec_ia(texte):
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": f"""Extrait les informations suivantes de cette facture et réponds UNIQUEMENT en JSON valide, rien d'autre :
{{
    "numero_facture": "...",
    "date": "...",
    "echeance": "...",
    "total_ht": "...",
    "tva": "...",
    "total_ttc": "..."
}}

Si une information est absente, mets "Non trouvé".

Facture :
{texte}"""
            }
        ]
    )
    
    contenu = message.content[0].text
    contenu = re.sub(r'```json|```', '', contenu).strip()
    data = json.loads(contenu)
    
    return {
        "Numéro facture": data.get("numero_facture", "Non trouvé"),
        "Date": data.get("date", "Non trouvé"),
        "Échéance": data.get("echeance", "Non trouvé"),
        "Total HT": data.get("total_ht", "Non trouvé"),
        "TVA": data.get("tva", "Non trouvé"),
        "Total TTC": data.get("total_ttc", "Non trouvé"),
    }

st.title("Extracteur de factures PDF")
st.write("Uploadez une facture PDF et obtenez vos données en Excel automatiquement")

fichier = st.file_uploader("Choisir un PDF", type="pdf")

if fichier:
    with pdfplumber.open(fichier) as pdf:
        texte = ""
        for page in pdf.pages:
            texte += page.extract_text()
    st.text_area("Texte extrait du PDF", texte, height=200)
    with st.spinner("Extraction en cours..."):
        resultat = extraire_avec_ia(texte)
    
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
