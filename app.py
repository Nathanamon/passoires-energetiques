import streamlit as st
import pandas as pd
from sections.intro import show_intro
from sections.overview import show_overview
from sections.deep_dives import show_deep_dives
from sections.conclusions import show_conclusions
from utils.io import load_data
from utils.prep import prepare_data
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="Rénovation Énergétique du Parc Social",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #3B82F6;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 20px;
        border-left: 5px solid #3B82F6;
        margin-bottom: 15px;
    }
    .info-box {
        background-color: #EFF6FF;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #93C5FD;
        margin: 10px 0;
    }
    .warning-box {
        background-color: #FEF3C7;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #F59E0B;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_and_prepare():
    """Charge et prépare les données"""
    df = load_data()
    df_clean = prepare_data(df)
    return df_clean

def main():
    # Titre principal
    st.markdown('<h1 class="main-header">Rénovation Énergétique du Parc Social</h1>', 
                unsafe_allow_html=True)
    st.markdown("### Priorité aux Passoires Thermiques")
    
    # Barre latérale pour la navigation
    st.sidebar.image("data/FullSizeRender.jpg", 
                     width=100)
    st.sidebar.title("Navigation")
    
    page = st.sidebar.radio(
        "Sections",
        ["Introduction & Contexte", 
         "Vue d'ensemble", 
         "Analyses approfondies", 
         "Conclusions & Priorités"]
    )
    
    # Chargement des données avec indicateur de progression
    with st.spinner("Chargement des données..."):
        data = load_and_prepare()
    
    # Affichage des métadonnées dans la sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Métadonnées")
    st.sidebar.info(f"**{len(data)}** départements analysés")
    st.sidebar.info(f"**{data['année_publication'].nunique()}** années de données")
    
    # Navigation entre les pages
    if page == "Introduction & Contexte":
        show_intro(data)
    elif page == "Vue d'ensemble":
        show_overview(data)
    elif page == "Analyses approfondies":
        show_deep_dives(data)
    elif page == "Conclusions & Priorités":
        show_conclusions(data)
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption("Source : Données ouvertes françaises")
    with col2:
        st.caption("Thème : Rénovation énergétique")
    with col3:
        st.caption("Objectif : Identifier les priorités")

if __name__ == "__main__":
    main()