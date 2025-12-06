import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.viz import create_map, create_radar_chart
import numpy as np

def show_deep_dives(data):
    """Affiche les analyses approfondies"""
    
    st.markdown('<h2 class="sub-header">Analyses Approfondies</h2>', 
                unsafe_allow_html=True)
    
    # Filtres avancés
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Filtres avancés")
    
    # Sélection de l'indicateur principal
    indicateur_principal = st.sidebar.selectbox(
        "Indicateur principal à analyser",
        options=[
            'Parc social - Taux de logements énergivores (E,F,G)* (en %)',
            'Parc social - Âge moyen du parc  (en années)',
            'Taux de pauvreté* (en %)',
            'Parc social - Loyer moyen (en €/m²/mois)*'
        ],
        index=0
    )
    
    # Seuil pour les passoires thermiques
    seuil_energivore = st.sidebar.slider(
        "Seuil passoires thermiques (%)",
        min_value=0,
        max_value=50,
        value=15,
        help="Définition du seuil pour les départements prioritaires"
    )
    
    # Calcul des indicateurs dérivés
    data_analysis = data.copy()
    
    # Catégorisation des départements
    data_analysis['Priorité'] = pd.cut(
        data_analysis['Parc social - Taux de logements énergivores (E,F,G)* (en %)'],
        bins=[0, 10, 20, 30, 100],
        labels=['Basse', 'Moyenne', 'Haute', 'Très haute'],
        include_lowest=True
    )
    
    # Indice composite de priorité
    data_analysis['Indice_priorité'] = (
        data_analysis['Parc social - Taux de logements énergivores (E,F,G)* (en %)'] * 0.4 +
        data_analysis['Taux de pauvreté* (en %)'] * 0.3 +
        (data_analysis['Parc social - Âge moyen du parc  (en années)'] / 50) * 0.3
    )
    
    # Normalisation pour la carte
    data_analysis['Indice_norm'] = (
        data_analysis['Indice_priorité'] - data_analysis['Indice_priorité'].min()
    ) / (data_analysis['Indice_priorité'].max() - data_analysis['Indice_priorité'].min())
    
    # Carte interactive
    st.markdown("### Carte des Priorités de Rénovation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Création de la carte avec Plotly
        fig = px.choropleth(
            data_analysis,
            geojson="https://raw.githubusercontent.com/gregoiredavid/france-geojson/master/departements.geojson",
            locations='code_departement',
            featureidkey="properties.code",
            color='Indice_norm',
            color_continuous_scale="Reds",
            range_color=(0, 1),
            scope="europe",
            center={"lat": 46.5, "lon": 2},
            hover_name='nom_departement',
            hover_data={
                'Parc social - Taux de logements énergivores (E,F,G)* (en %)': ':.1f%',
                'Parc social - Âge moyen du parc  (en années)': ':.0f ans',
                'Taux de pauvreté* (en %)': ':.1f%',
                'Priorité': True
            },
            labels={'Indice_norm': 'Indice de priorité'},
            title="Carte de priorité des rénovations énergétiques"
        )
        
        fig.update_geos(
            fitbounds="locations",
            visible=False,
            projection_type="mercator",
            center=dict(lon=2, lat=46.5),
            lataxis_range=[41, 51],
            lonaxis_range=[-5, 10]
        )
        
        fig.update_layout(
            margin={"r":0,"t":30,"l":0,"b":0},
            height=600,
            coloraxis_colorbar=dict(
                title="Priorité",
                tickvals=[0, 0.25, 0.5, 0.75, 1],
                ticktext=["Très faible", "Faible", "Moyenne", "Élevée", "Très élevée"]
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### Légende de priorité")
        
        for priorite, couleur in [('Très haute', '#DC2626'), 
                                  ('Haute', '#EF4444'), 
                                  ('Moyenne', '#FCA5A5'), 
                                  ('Basse', '#FECACA')]:
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin: 5px 0;">
                <div style="width: 20px; height: 20px; background-color: {couleur}; 
                     margin-right: 10px; border-radius: 3px;"></div>
                <span>{priorite}</span>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("#### Départements prioritaires")
        
        # Top 5 des départements prioritaires
        top_prioritaires = data_analysis.nlargest(5, 'Indice_priorité')
        
        for idx, row in top_prioritaires.iterrows():
            st.metric(
                label=row['nom_departement'],
                value=f"{row['Parc social - Taux de logements énergivores (E,F,G)* (en %)']:.1f}%",
                delta=f"Priorité {row['Priorité']}"
            )
    
    # Analyse temporelle
    st.markdown("### Évolution Temporelle")
    
    if 'année_publication' in data.columns and data['année_publication'].nunique() > 1:
        # Préparation des données temporelles
        evolution = data.groupby('année_publication').agg({
            'Parc social - Taux de logements énergivores (E,F,G)* (en %)': 'mean',
            'Parc social - Âge moyen du parc  (en années)': 'mean',
            'nom_departement': 'count'
        }).reset_index()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.line(
                evolution,
                x='année_publication',
                y='Parc social - Taux de logements énergivores (E,F,G)* (en %)',
                title="Évolution du taux de passoires thermiques",
                markers=True
            )
            fig.update_layout(
                xaxis_title="Année",
                yaxis_title="Taux moyen (%)",
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.line(
                evolution,
                x='année_publication',
                y='Parc social - Âge moyen du parc  (en années)',
                title="Évolution de l'âge moyen du parc",
                markers=True
            )
            fig.update_layout(
                xaxis_title="Année",
                yaxis_title="Âge moyen (années)",
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Analyse multivariée
    st.markdown("### Analyse Multidimensionnelle")
    
    # Sélection des variables pour l'analyse
    variables = st.multiselect(
        "Sélectionnez les variables à comparer",
        options=[
            'Parc social - Taux de logements énergivores (E,F,G)* (en %)',
            'Parc social - Âge moyen du parc  (en années)',
            'Taux de pauvreté* (en %)',
            'Parc social - Loyer moyen (en €/m²/mois)*',
            'Taux de chômage au T4 (en %)',
            'Densité de population au km²'
        ],
        default=[
            'Parc social - Taux de logements énergivores (E,F,G)* (en %)',
            'Parc social - Âge moyen du parc  (en années)',
            'Taux de pauvreté* (en %)'
        ]
    )
    
    if len(variables) >= 2:
        tab1, tab2 = st.tabs(["Matrice de corrélation", "Nuage de points"])
        
        with tab1:
            # Matrice de corrélation
            corr_matrix = data[variables].corr().round(2)
            
            fig = px.imshow(
                corr_matrix,
                text_auto=True,
                color_continuous_scale='RdBu_r',
                title="Matrice de corrélation entre les indicateurs",
                aspect="auto"
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Nuage de points 3D si 3 variables sélectionnées
            if len(variables) == 3:
                fig = px.scatter_3d(
                    data,
                    x=variables[0],
                    y=variables[1],
                    z=variables[2],
                    color='Parc social - Taux de logements énergivores (E,F,G)* (en %)',
                    hover_name='nom_departement',
                    title="Visualisation 3D des relations",
                    color_continuous_scale='Reds'
                )
                fig.update_layout(height=600)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sélectionnez exactement 3 variables pour la visualisation 3D")
    
    # Analyse par typologie
    st.markdown("### Typologie des Départements")
    
    # Classification simple basée sur deux critères
    data_analysis['Typologie'] = pd.cut(
        data_analysis['Parc social - Taux de logements énergivores (E,F,G)* (en %)'],
        bins=[0, 10, 20, 100],
        labels=['Performants', 'Intermédiaires', 'Prioritaires']
    )
    
    typologie_stats = data_analysis.groupby('Typologie').agg({
        'nom_departement': 'count',
        'Parc social - Taux de logements énergivores (E,F,G)* (en %)': 'mean',
        'Parc social - Âge moyen du parc  (en années)': 'mean',
        'Taux de pauvreté* (en %)': 'mean'
    }).round(1)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.dataframe(typologie_stats, use_container_width=True)
    
    with col2:
        # Nettoyage pour éviter l'erreur "None entries cannot have not-None children"
        sunburst_df = data_analysis.copy()
        # garder uniquement les lignes où les niveaux hiérarchiques sont présents
        sunburst_df = sunburst_df.dropna(subset=['Typologie', 'nom_region'])
        # Option alternative si vous préférez garder toutes les lignes :
        # sunburst_df['Typologie'] = sunburst_df['Typologie'].fillna('Inconnu')
        
        fig = px.sunburst(
            sunburst_df,
            path=['Typologie', 'nom_region'],
            # values='code_departement',  # supprimé : provoquait l'erreur (non numérique)
            title="Répartition des départements par typologie et région",
            color='Parc social - Taux de logements énergivores (E,F,G)* (en %)',
            color_continuous_scale='Reds'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    # Export des analyses
    st.markdown("### Export des Données")
    
    if st.button("Exporter les données analysées"):
        csv = data_analysis.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Télécharger CSV",
            data=csv,
            file_name="analyse_renovation_energetique.csv",
            mime="text/csv"
        )