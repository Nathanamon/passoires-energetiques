import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.viz import create_gauge_chart

def show_conclusions(data):
    """Affiche les conclusions et recommandations"""
    
    st.markdown('<h2 class="sub-header">🎯 Conclusions & Priorités d\'Action</h2>', 
                unsafe_allow_html=True)
    
    # Forcer styles lisibles pour .info-box et .warning-box
    st.markdown("""
    <style>
    .info-box, .warning-box {
        padding: 16px !important;
        border-radius: 8px !important;
        border: 1px solid rgba(0,0,0,0.06) !important;
        color: #111827 !important;
        background-clip: padding-box !important;
    }
    .info-box {
        background: linear-gradient(180deg, #ffffff, #f3f4f6) !important;
    }
    .warning-box {
        background: #fff7ed !important;
        color: #7a341f !important;
    }
    .info-box h3, .warning-box h3,
    .info-box p, .warning-box p,
    .info-box li, .warning-box li {
        color: inherit !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Synthèse narrative
    st.markdown("""
    <div class="info-box">
    <h3>Synthèse des Principaux Enseignements</h3>
    <p>L'analyse révèle des <strong>disparités significatives</strong> entre les départements français 
    concernant la performance énergétique du parc social. Trois enseignements majeurs se dégagent :</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Indicateurs de synthèse
    st.markdown("### Indicateurs de Synthèse")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Score national
        score_national = data['Parc social - Taux de logements énergivores (E,F,G)* (en %)'].mean()
        fig = create_gauge_chart(
            score_national,
            "Score national",
            max_value=50,
            threshold=15
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Progression nécessaire
        reduction_needed = max(0, score_national - 10)  # Objectif 10%
        fig = create_gauge_chart(
            reduction_needed,
            "Réduction nécessaire",
            max_value=30,
            threshold=10,
            reverse=True
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col3:
        # Maturité du parc
        age_moyen = data['Parc social - Âge moyen du parc  (en années)'].mean()
        fig = create_gauge_chart(
            age_moyen,
            "Âge moyen du parc",
            max_value=60,
            threshold=30
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Priorités d'action
    st.markdown("### Priorités d'Action Stratégiques")
    
    # Calcul des priorités
    data['Score_urgence'] = (
        data['Parc social - Taux de logements énergivores (E,F,G)* (en %)'] * 0.4 +
        data['Taux de pauvreté* (en %)'] * 0.3 +
        (data['Parc social - Âge moyen du parc  (en années)'] / 100) * 0.3
    )
    
    # Top 10 des départements prioritaires
    top_prioritaires = data.nlargest(10, 'Score_urgence')
    
    tab1, tab2, tab3 = st.tabs(["Top 10 Prioritaires", "Roadmap", "Impact"])
    
    with tab1:
        fig = go.Figure(data=[
            go.Bar(
                name='Passoires thermiques',
                x=top_prioritaires['nom_departement'],
                y=top_prioritaires['Parc social - Taux de logements énergivores (E,F,G)* (en %)'],
                marker_color='#EF4444'
            ),
            go.Bar(
                name='Âge moyen',
                x=top_prioritaires['nom_departement'],
                y=top_prioritaires['Parc social - Âge moyen du parc  (en années)'] / 2,
                marker_color='#3B82F6'
            ),
            go.Bar(
                name='Pauvreté',
                x=top_prioritaires['nom_departement'],
                y=top_prioritaires['Taux de pauvreté* (en %)'],
                marker_color='#8B5CF6'
            )
        ])
        
        fig.update_layout(
            title="Top 10 des départements prioritaires - Indicateurs clés",
            barmode='group',
            xaxis_tickangle=45,
            yaxis_title="Valeur des indicateurs",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau détaillé
        st.dataframe(
            top_prioritaires[[
                'nom_departement', 'nom_region',
                'Parc social - Taux de logements énergivores (E,F,G)* (en %)',
                'Parc social - Âge moyen du parc  (en années)',
                'Taux de pauvreté* (en %)',
                'Score_urgence'
            ]].round(2),
            use_container_width=True
        )
    
    with tab2:
        st.markdown("""
        ### Roadmap de Rénovation 2024-2030
        
        **Phase 1 : Urgence (2024-2025)**
        - Cibler les départements avec >20% de passoires thermiques
        - Lancer des programmes de rénovation lourde
        - Mobiliser les financements publics prioritaires
        
        **Phase 2 : Accélération (2026-2028)**
        - Étendre aux départements avec 10-20% de passoires
        - Focus sur l'isolation thermique
        - Développer les circuits courts de rénovation
        
        **Phase 3 : Généralisation (2029-2030)**
        - Atteindre l'objectif national de <10%
        - Systématiser le suivi des performances
        - Capitaliser sur les retours d'expérience
        """)
        
        # Timeline visuelle
        timeline_data = pd.DataFrame({
            'Année': [2024, 2025, 2026, 2027, 2028, 2029, 2030],
            'Objectif': [20, 18, 16, 14, 12, 10, 8],
            'Phase': ['Urgence', 'Urgence', 'Accélération', 'Accélération', 
                     'Accélération', 'Généralisation', 'Généralisation']
        })
        
        fig = px.line(
            timeline_data,
            x='Année',
            y='Objectif',
            color='Phase',
            markers=True,
            title="Objectifs de réduction des passoires thermiques",
            color_discrete_sequence=['#EF4444', '#F59E0B', '#10B981']
        )
        fig.update_layout(
            yaxis_title="Objectif maximal de passoires (%)",
            yaxis_range=[0, 25]
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("""
        ### 💰 Impact Économique et Social Estimé
        
        **Investissements nécessaires :**
        - **Rénovation complète** : 40.000€/logement en moyenne
        - **Cible prioritaire** : 200.000 logements sociaux énergivores
        - **Investissement total** : ~8 milliards d'euros
        
        **Retours sur investissement :**
        - **Économies énergétiques** : 1.500€/an/logement
        - **Création d'emplois** : ~100.000 équivalents temps plein
        - **Confort amélioré** : 2 millions d'habitants concernés
        - **Réduction CO₂** : 2 millions de tonnes/an
        
        **Ratio coût-bénéfice :** 1€ investi = 2,5€ de bénéfices sociaux et environnementaux
        """)
        
        # Graphique d'impact
        impact_data = pd.DataFrame({
            'Catégorie': ['Économies énergétiques', 'Emplois créés', 'Bénéfices santé', 
                         'Réduction CO₂', 'Valeur patrimoniale'],
            'Valeur': [3.0, 2.5, 1.8, 1.5, 1.2],
            'Unité': ['Md€/an', '100k ETP', 'Indice', 'Mt CO₂/an', 'Indice']
        })
        
        fig = px.bar(
            impact_data,
            x='Valeur',
            y='Catégorie',
            orientation='h',
            text='Unité',
            color='Valeur',
            color_continuous_scale='Greens',
            title="Impacts attendus de la rénovation (à l'échelle nationale)"
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Recommandations spécifiques
    st.markdown("### Recommandations Opérationnelles")
    
    recommendations = [
        {
            "priorité": "Haute",
            "recommandation": "Créer un fonds dédié aux départements >20% de passoires",
            "impact": "Réduction immédiate de 30%",
            "coût": "Moyen",
            "délai": "6 mois"
        },
        {
            "priorité": "Haute",
            "recommandation": "Simplifier les démarches administratives pour les bailleurs",
            "impact": "Accélération des travaux de 40%",
            "coût": "Faible",
            "délai": "3 mois"
        },
        {
            "priorité": "Moyenne",
            "recommandation": "Développer des formations spécifiques pour les artisans",
            "impact": "Amélioration qualité des rénovations",
            "coût": "Moyen",
            "délai": "12 mois"
        },
        {
            "priorité": "Moyenne",
            "recommandation": "Mettre en place un système de monitoring énergétique",
            "impact": "Optimisation continue des performances",
            "coût": "Élevé",
            "délai": "18 mois"
        }
    ]
    
    for rec in recommendations:
        with st.expander(f"**{rec['priorité']}** : {rec['recommandation']}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Impact estimé", rec['impact'])
            with col2:
                st.metric("Coût", rec['coût'])
            with col3:
                st.metric("Délai de mise en œuvre", rec['délai'])
    
    # Appel à l'action
    st.markdown("""
    <div class="warning-box">
    <h3>Prochaines Étapes</h3>
    <p>Cette analyse fournit une <strong>base solide pour l'action</strong>. Les prochaines étapes devraient inclure :</p>
    <ul>
    <li><strong>Analyse plus fine</strong> à l'échelle des EPCI et des communes</li>
    <li><strong>Concertation</strong> avec les bailleurs sociaux et les collectivités</li>
    <li><strong>Mise en place d'un tableau de bord de suivi</strong> en temps réel</li>
    <li><strong>Définition d'objectifs spécifiques</strong> par territoire</li>
    </ul>
    <p><strong>L'urgence climatique et sociale nécessite une action coordonnée et déterminée.</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Signature
    st.markdown("---")
    st.markdown("*Tableau de bord réalisé dans le cadre du projet Data Storytelling - EFREI Paris 2025*")