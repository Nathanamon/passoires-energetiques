import streamlit as st
import pandas as pd
import numpy as np
import requests
from io import StringIO
import json

@st.cache_data(ttl=3600, show_spinner="Chargement des données...")
def load_data():
    """
    Charge les données depuis le fichier CSV local ou une URL
    """
    try:
        # Pour l'exemple, on utilise les données fournies dans l'extrait
        # En production, vous remplacerez par le chemin vers votre fichier complet
        data = pd.read_csv('data/logements-et-logements-sociaux-dans-les-departements.csv', 
                          sep=';', encoding='utf-8')
        
        # Nettoyage des noms de colonnes
        data.columns = data.columns.str.strip()
        
        # Conversion des types de données
        numeric_columns = [
            'Nombre  d\'habitants',
            'Densité de population au km²',
            'Variation de la population sur 10 ans (en %)',
            'Dont contribution du solde naturel (en %)',
            'Dont contribution du solde migratoire (en %)',
            '% population de moins de 20 ans',
            '% population de 60 ans et plus',
            'Taux de chômage au T4 (en %)',
            'Taux de pauvreté* (en %)',
            'Nombre de logements',
            'Nombre de résidences principales',
            'Taux de logements sociaux* (en %)',
            'Taux de logements vacants* (en %)',
            'Taux de logements individuels (en %)',
            'Moyenne annuelle de la construction neuve sur 10 ans',
            'Construction',
            'Parc social - Nombre de logements',
            'Parc social - Logements mis en location*',
            'Parc social - Logements démolis',
            'Parc social - Ventes à des personnes physiques',
            'Parc social - Taux de logements vacants* (en %)',
            'Parc social - Taux de logements individuels (en %)',
            'Parc social - Loyer moyen (en €/m²/mois)*',
            'Parc social - Âge moyen du parc  (en années)',
            'Parc social - Taux de logements énergivores (E,F,G)* (en %)'
        ]
        
        for col in numeric_columns:
            if col in data.columns:
                # Remplacement des virgules par des points et conversion en numérique
                data[col] = pd.to_numeric(data[col].astype(str).str.replace(',', '.'), 
                                         errors='coerce')
        
        # Conversion de l'année en entier
        if 'année_publication' in data.columns:
            data['année_publication'] = pd.to_numeric(data['année_publication'], 
                                                     errors='coerce').fillna(2023).astype(int)
        
        return data
        
    except FileNotFoundError:
        st.error("Fichier de données non trouvé. Utilisation des données d'exemple.")
        
        # Création de données d'exemple basées sur l'extrait fourni
        sample_data = create_sample_data()
        return sample_data

def create_sample_data():
    """Crée des données d'exemple basées sur l'extrait fourni"""
    # Cette fonction crée un jeu de données plus complet pour la démonstration
    # Basé sur les 10 lignes fournies dans l'extrait
    
    data = {
        'année_publication': [2023, 2022, 2022, 2022, 2022, 2021, 2021, 2021, 2020, 2019],
        'code_departement': ['36', '11', '22', '74', '21', '972', '69', '50', '24', '07'],
        'nom_departement': ['Indre', 'Aude', 'Côtes-d\'Armor', 'Haute-Savoie', 'Côte-d\'Or', 
                           'Martinique', 'Rhône', 'Manche', 'Dordogne', 'Ardèche'],
        'code_region': ['24', '76', '53', '84', '27', '02', '84', '28', '75', '84'],
        'nom_region': ['CENTRE-VAL DE LOIRE', 'OCCITANIE', 'BRETAGNE', 
                      'AUVERGNE-RHÔNE-ALPES', 'BOURGOGNE-FRANCHE-COMTÉ', 
                      'MARTINIQUE', 'AUVERGNE-RHÔNE-ALPES', 'NORMANDIE', 
                      'NOUVELLE-AQUITAINE', 'AUVERGNE-RHÔNE-ALPES'],
        'Nombre  d\'habitants': [217378, 378068, 600924, 841639, 534164, 363484, 1882578, 492896, 411495, 326632],
        'Parc social - Taux de logements énergivores (E,F,G)* (en %)': [26.0, 9.0, 13.0, 14.0, 16.0, 0.0, 23.0, 34.0, 12.0, 34.0],
        'Parc social - Âge moyen du parc  (en années)': [39.0, 38.0, 32.0, 28.0, 35.0, 25.0, 40.0, 42.0, 34.0, 36.0],
        'Taux de pauvreté* (en %)': [14.6, 20.0, 12.1, 9.4, 11.5, 28.6, 14.2, 12.0, 16.0, 14.0],
        'Parc social - Loyer moyen (en €/m²/mois)*': [5.31, 5.47, 5.11, 6.33, 5.77, 5.6, 6.12, 4.73, 5.2, 5.1],
        'Taux de chômage au T4 (en %)': [7.0, 10.5, 6.8, 6.5, 5.8, 15.0, 7.3, 5.8, 9.0, 9.0],
        'Densité de population au km²': [32.0, 61.0, 87.0, 190.0, 61.0, 322.0, 579.0, 83.0, 45.0, 59.0]
    }
    
    # Ajout de données synthétiques pour compléter
    df = pd.DataFrame(data)
    
    # Ajout de variations pour simuler un jeu de données plus complet
    np.random.seed(42)
    n_rows = 100
    
    expanded_data = []
    for _ in range(n_rows):
        base_row = df.sample(1).iloc[0].copy()
        
        # Ajout de variations aléatoires
        base_row['Parc social - Taux de logements énergivores (E,F,G)* (en %)'] = np.random.uniform(0, 40)
        base_row['Parc social - Âge moyen du parc  (en années)'] = np.random.uniform(20, 50)
        base_row['Taux de pauvreté* (en %)'] = np.random.uniform(5, 30)
        base_row['Nombre  d\'habitants'] = np.random.randint(100000, 2000000)
        
        expanded_data.append(base_row)
    
    final_df = pd.DataFrame(expanded_data)
    
    # Ajout de coordonnées géographiques approximatives
    regions_coords = {
        'CENTRE-VAL DE LOIRE': {'lat': 47.5, 'lon': 1.75},
        'OCCITANIE': {'lat': 43.5, 'lon': 2.0},
        'BRETAGNE': {'lat': 48.2, 'lon': -2.75},
        'AUVERGNE-RHÔNE-ALPES': {'lat': 45.5, 'lon': 4.5},
        'BOURGOGNE-FRANCHE-COMTÉ': {'lat': 47.0, 'lon': 4.5},
        'MARTINIQUE': {'lat': 14.6, 'lon': -61.0},
        'NORMANDIE': {'lat': 49.0, 'lon': 0.0},
        'NOUVELLE-AQUITAINE': {'lat': 45.0, 'lon': 0.5}
    }
    
    final_df['latitude'] = final_df['nom_region'].map(lambda x: regions_coords.get(x, {'lat': 46.0})['lat'])
    final_df['longitude'] = final_df['nom_region'].map(lambda x: regions_coords.get(x, {'lon': 2.0})['lon'])
    
    return final_df

def get_data_info(data):
    """Retourne des informations sur les données"""
    info = {
        'nombre_lignes': len(data),
        'nombre_colonnes': len(data.columns),
        'colonnes': list(data.columns),
        'types_donnees': data.dtypes.to_dict(),
        'valeurs_manquantes': data.isnull().sum().to_dict()
    }
    return info

def save_analysis_results(data, filename):
    """Sauvegarde les résultats d'analyse"""
    data.to_csv(f"data/{filename}", index=False, encoding='utf-8')
    return True