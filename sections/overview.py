import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.viz import create_metric_card, create_distribution_chart

def show_overview(data):
    """Affiche la vue d'ensemble"""
    
    st.markdown('<h2 class="sub-header">Vue d\'ensemble Nationale</h2>', 
                unsafe_allow_html=True)
    
    # Filtres dans la sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Filtres d'analyse")
    
    # Sélection de l'année
    annees = sorted(data['année_publication'].unique(), reverse=True)
    annee_selection = st.sidebar.select_slider(
        "Année d'analyse",
        options=annees,
        value=max(annees)
    )
    
    # Filtre par région
    regions = sorted(data['nom_region'].unique())
    region_selection = st.sidebar.multiselect(
        "Régions",
        options=regions,
        default=regions[:3] if len(regions) > 3 else regions
    )
    
    # Application des filtres
    data_filtered = data[
        (data['année_publication'] == annee_selection) &
        (data['nom_region'].isin(region_selection) if region_selection else True)
    ]
    
    # KPI en haut de page
    st.markdown("### Indicateurs Clés de Performance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        taux_energivore = data_filtered['Parc social - Taux de logements énergivores (E,F,G)* (en %)'].mean()
        create_metric_card(
            "Passoires thermiques",
            f"{taux_energivore:.1f}%",
            f"Moyenne nationale - {len(data_filtered)} départements",
            "danger" if taux_energivore > 15 else "warning" if taux_energivore > 10 else "success"
        )
    
    with col2:
        age_moyen = data_filtered['Parc social - Âge moyen du parc  (en années)'].mean()
        create_metric_card(
            "Âge moyen du parc",
            f"{age_moyen:.0f} ans",
            "Corrélé avec la performance énergétique",
            "warning" if age_moyen > 35 else "info"
        )
    
    with col3:
        pauvreté_moyenne = data_filtered['Taux de pauvreté* (en %)'].mean()
        create_metric_card(
            "Taux de pauvreté",
            f"{pauvreté_moyenne:.1f}%",
            "Contexte socio-économique",
            "danger" if pauvreté_moyenne > 20 else "warning"
        )
    
    with col4:
        logements_sociaux = data_filtered['Taux de logements sociaux* (en %)'].mean()
        create_metric_card(
            "Taux de logements sociaux",
            f"{logements_sociaux:.1f}%",
            "Part du parc social",
            "info"
        )
    
    # Distribution nationale
    st.markdown("### Distribution Nationale des Passoires Thermiques")
    
    tab1, tab2, tab3 = st.tabs(["Histogramme", "Top 10", "Par région"])
    
    with tab1:
        fig = px.histogram(
            data_filtered,
            x='Parc social - Taux de logements énergivores (E,F,G)* (en %)',
            nbins=30,
            title="Distribution du taux de passoires thermiques",
            labels={'Parc social - Taux de logements énergivores (E,F,G)* (en %)': 'Taux de passoires thermiques (%)'},
            color_discrete_sequence=['#EF4444']
        )
        fig.update_layout(
            showlegend=False,
            xaxis_title="Taux de logements énergivores (%)",
            yaxis_title="Nombre de départements"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        # Top 10 des départements avec le plus de passoires thermiques
        top10 = data_filtered.nlargest(10, 'Parc social - Taux de logements énergivores (E,F,G)* (en %)')
        
        fig = px.bar(
            top10,
            x='Parc social - Taux de logements énergivores (E,F,G)* (en %)',
            y='nom_departement',
            orientation='h',
            title="Top 10 - Départements avec le plus de passoires thermiques",
            color='Parc social - Taux de logements énergivores (E,F,G)* (en %)',
            color_continuous_scale='Reds',
            text='Parc social - Taux de logements énergivores (E,F,G)* (en %)'
        )
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            xaxis_title="Taux de passoires thermiques (%)",
            yaxis_title="Département"
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Vue par région
        region_stats = data_filtered.groupby('nom_region').agg({
            'Parc social - Taux de logements énergivores (E,F,G)* (en %)': 'mean',
            'nom_departement': 'count'
        }).round(1).reset_index()
        region_stats = region_stats.rename(columns={'nom_departement': 'Nombre de départements'})
        
        fig = px.bar(
            region_stats,
            x='nom_region',
            y='Parc social - Taux de logements énergivores (E,F,G)* (en %)',
            title="Taux moyen de passoires thermiques par région",
            color='Parc social - Taux de logements énergivores (E,F,G)* (en %)',
            color_continuous_scale='Reds',
            text='Parc social - Taux de logements énergivores (E,F,G)* (en %)',
            hover_data=['Nombre de départements']
        )
        fig.update_layout(
            xaxis_title="Région",
            yaxis_title="Taux moyen de passoires thermiques (%)",
            xaxis_tickangle=45
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    # Analyse de corrélation
    st.markdown("### Relations Clés")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Corrélation âge vs énergivores
        fig = px.scatter(
            data_filtered,
            x='Parc social - Âge moyen du parc  (en années)',
            y='Parc social - Taux de logements énergivores (E,F,G)* (en %)',
            trendline="ols",
            title="Âge du parc vs Passoires thermiques",
            hover_data=['nom_departement', 'nom_region'],
            labels={
                'Parc social - Âge moyen du parc  (en années)': 'Âge moyen du parc (années)',
                'Parc social - Taux de logements énergivores (E,F,G)* (en %)': 'Taux de passoires thermiques (%)'
            }
        )
        fig.update_traces(marker=dict(size=10, opacity=0.7))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Corrélation pauvreté vs énergivores
        fig = px.scatter(
            data_filtered,
            x='Taux de pauvreté* (en %)',
            y='Parc social - Taux de logements énergivores (E,F,G)* (en %)',
            trendline="ols",
            title="Pauvreté vs Passoires thermiques",
            hover_data=['nom_departement', 'nom_region'],
            labels={
                'Taux de pauvreté* (en %)': 'Taux de pauvreté (%)',
                'Parc social - Taux de logements énergivores (E,F,G)* (en %)': 'Taux de passoires thermiques (%)'
            }
        )
        fig.update_traces(marker=dict(size=10, opacity=0.7))
        st.plotly_chart(fig, use_container_width=True)
    
    # Tableau interactif
    st.markdown("### Données Détailées")
    
    if st.checkbox("Afficher le tableau des données filtrées"):
        columns_to_show = [
            'nom_departement', 'nom_region', 'année_publication',
            'Parc social - Taux de logements énergivores (E,F,G)* (en %)',
            'Parc social - Âge moyen du parc  (en années)',
            'Taux de pauvreté* (en %)',
            'Parc social - Loyer moyen (en €/m²/mois)*'
        ]
        
        display_df = data_filtered[columns_to_show].copy()
        display_df = display_df.round(1)
        
        # Formatage des pourcentages
        for col in display_df.columns:
            if '%' in col:
                display_df[col] = display_df[col].astype(str) + '%'
        
        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                'nom_departement': st.column_config.TextColumn("Département"),
                'nom_region': st.column_config.TextColumn("Région"),
                'année_publication': st.column_config.NumberColumn("Année"),
                'Parc social - Taux de logements énergivores (E,F,G)* (en %)': 
                    st.column_config.ProgressColumn(
                        "Passoires thermiques",
                        help="Taux de logements énergivores (E, F, G)",
                        format="%f%%",
                        min_value=0,
                        max_value=100
                    )
            }
        )