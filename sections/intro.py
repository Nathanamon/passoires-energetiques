import streamlit as st
import pandas as pd

def show_intro(data):
    """Affiche la section d'introduction"""
    
    st.markdown('<h2 class="sub-header">Introduction & Contexte</h2>', 
                unsafe_allow_html=True)
    
    # Ajout de CSS pour forcer fond et couleur lisible
    st.markdown("""
    <style>
    .info-box {
        background: linear-gradient(180deg, #ffffff, #f3f4f6);
        color: #111827 !important;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid rgba(0,0,0,0.06);
    }
    .warning-box {
        background: #fff7ed;
        color: #7a341f !important;
        padding: 16px;
        border-radius: 8px;
        border: 1px solid rgba(0,0,0,0.06);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Introduction narrative
    st.markdown("""
    <div class="info-box">
    <h4>Le Défi des Passoires Thermiques</h4>
    <p>En France, <strong>millions de logements</strong> sont considérés comme des "passoires thermiques" 
    (classes énergétiques E, F, G). Ces logements représentent un enjeu majeur :</p>
    <ul>
    <li><strong>Confort dégradé</strong> pour les occupants</li>
    <li><strong>Factures énergétiques élevées</strong> (précarité énergétique)</li>
    <li><strong>Impact environnemental important</strong> (émissions de CO₂)</li>
    <li><strong>Inégalités sociales accentuées</strong></li>
    </ul>
    <p>Le <strong>parc social</strong> joue un rôle crucial dans cette transition écologique.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Statistiques clés
    st.markdown("### Quelques Chiffres Clés")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        taux_moyen = data['Parc social - Taux de logements énergivores (E,F,G)* (en %)'].mean()
        st.metric(
            label="Passoires thermiques (moyenne)",
            value=f"{taux_moyen:.1f}%",
            delta=f"-{taux_moyen*0.1:.1f}% objectif 2030" if taux_moyen > 0 else None
        )
    
    with col2:
        age_moyen = data['Parc social - Âge moyen du parc  (en années)'].mean()
        st.metric(
            label="Âge moyen du parc",
            value=f"{age_moyen:.0f} ans",
            delta=f"+{data['Parc social - Âge moyen du parc  (en années)'].std():.0f} ans écart-type"
        )
    
    with col3:
        taux_vacants = data['Parc social - Taux de logements vacants* (en %)'].mean()
        st.metric(
            label="Logements sociaux vacants",
            value=f"{taux_vacants:.1f}%",
            delta_color="inverse"
        )
    
    with col4:
        loyer_moyen = data['Parc social - Loyer moyen (en €/m²/mois)*'].mean()
        st.metric(
            label="Loyer moyen (social)",
            value=f"{loyer_moyen:.2f}€/m²",
            delta=f"+{loyer_moyen*0.05:.2f}€ tendance"
        )
    
    # Cartographie des enjeux
    st.markdown("### Cartographie des Enjeux")
    
    tab1, tab2, tab3 = st.tabs(["Objectifs", "Méthodologie", "Données"])
    
    with tab1:
        st.markdown("""
        #### Objectifs de ce tableau de bord :
        
        1. **Identifier** les départements avec le plus fort taux de passoires thermiques
        2. **Analyser** le lien entre âge du parc et performance énergétique
        3. **Prioriser** les zones d'intervention pour la rénovation
        4. **Suivre** l'évolution dans le temps
        """)
    
    with tab2:
        st.markdown("""
        #### Méthodologie d'analyse :
        
        **Sources de données** :
        - Données ouvertes françaises (data.gouv.fr)
        - Statistiques annuelles par département
        - Données géolocalisées
        
        **Indicateurs calculés** :
        - Taux de logements énergivores (E, F, G)
        - Âge moyen du parc immobilier
        - Densité de passoires thermiques
        - Indice de priorité de rénovation
        """)
    
    with tab3:
        st.markdown("""
        #### Structure des données :
        """)
        
        # Aperçu des données
        if st.checkbox("Afficher un aperçu des données"):
            st.dataframe(data.head(10), use_container_width=True)
        
        # Description des colonnes clés
        st.markdown("""
        **Colonnes principales analysées :**
        - `Parc social - Taux de logements énergivores (E,F,G)* (en %)` : Indicateur clé
        - `Parc social - Âge moyen du parc` : Corrélation avec l'énergie
        - `nom_departement`, `nom_region` : Localisation
        - `année_publication` : Suivi temporel
        - `Taux de pauvreté* (en %)` : Contexte social
        """)
    
    # Avertissement sur les données
    st.markdown("""
    <div class="warning-box">
    <h4>Notes méthodologiques</h4>
    <p>Les données présentent certaines limites :</p>
    <ul>
    <li>Données disponibles jusqu'en 2023 pour certains départements</li>
    <li>Hétérogénéité des méthodes de collecte</li>
    <li>Certains départements d'outre-mer non représentés</li>
    <li>Données déclaratives avec possibles erreurs de mesure</li>
    </ul>
    <p>Les analyses doivent être interprétées avec ces limites en tête.</p>
    </div>
    """, unsafe_allow_html=True)