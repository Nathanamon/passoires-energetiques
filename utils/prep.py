import pandas as pd
import numpy as np
from datetime import datetime

def prepare_data(data):
    """
    Nettoie et prépare les données pour l'analyse
    """
    df = data.copy()
    
    # 1. Nettoyage des colonnes
    df.columns = df.columns.str.strip()
    
    # 2. Gestion des valeurs manquantes
    df = handle_missing_values(df)
    
    # 3. Création de nouvelles variables
    df = create_derived_variables(df)
    
    # 4. Normalisation des données
    df = normalize_data(df)
    
    # 5. Catégorisation
    df = categorize_data(df)
    
    return df

def handle_missing_values(df):
    """Gère les valeurs manquantes de manière appropriée"""
    
    # Pour les taux de passoires thermiques, remplacer par la médiane régionale
    if 'Parc social - Taux de logements énergivores (E,F,G)* (en %)' in df.columns:
        regional_median = df.groupby('nom_region')['Parc social - Taux de logements énergivores (E,F,G)* (en %)'].transform('median')
        df['Parc social - Taux de logements énergivores (E,F,G)* (en %)'].fillna(regional_median, inplace=True)
    
    # Pour l'âge moyen, remplacer par la médiane nationale
    if 'Parc social - Âge moyen du parc  (en années)' in df.columns:
        national_median = df['Parc social - Âge moyen du parc  (en années)'].median()
        df['Parc social - Âge moyen du parc  (en années)'].fillna(national_median, inplace=True)
    
    # Remplacer les autres valeurs numériques manquantes par 0
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    
    # Remplacer les valeurs textuelles manquantes par "Non spécifié"
    text_cols = df.select_dtypes(include=[object]).columns
    df[text_cols] = df[text_cols].fillna('Non spécifié')
    
    return df

def create_derived_variables(df):
    """Crée de nouvelles variables dérivées pour l'analyse"""
    
    # 1. Indice de priorité composite
    if all(col in df.columns for col in [
        'Parc social - Taux de logements énergivores (E,F,G)* (en %)',
        'Parc social - Âge moyen du parc  (en années)',
        'Taux de pauvreté* (en %)'
    ]):
        # Normalisation min-max pour chaque composante
        df['energivores_norm'] = normalize_minmax(df['Parc social - Taux de logements énergivores (E,F,G)* (en %)'])
        df['age_norm'] = normalize_minmax(df['Parc social - Âge moyen du parc  (en années)'])
        df['pauvrete_norm'] = normalize_minmax(df['Taux de pauvreté* (en %)'])
        
        # Indice composite pondéré
        df['indice_priorite'] = (
            df['energivores_norm'] * 0.5 +
            df['age_norm'] * 0.3 +
            df['pauvrete_norm'] * 0.2
        )
    
    # 2. Catégorisation des départements
    if 'Parc social - Taux de logements énergivores (E,F,G)* (en %)' in df.columns:
        conditions = [
            df['Parc social - Taux de logements énergivores (E,F,G)* (en %)'] < 10,
            df['Parc social - Taux de logements énergivores (E,F,G)* (en %)'] < 20,
            df['Parc social - Taux de logements énergivores (E,F,G)* (en %)'] < 30,
            df['Parc social - Taux de logements énergivores (E,F,G)* (en %)'] >= 30
        ]
        choices = ['Faible', 'Moyen', 'Élevé', 'Très élevé']
        df['categorie_energivore'] = np.select(conditions, choices, default='Non classé')
    
    # 3. Ratio logements sociaux / population
    if all(col in df.columns for col in ['Nombre  d\'habitants', 'Parc social - Nombre de logements']):
        df['ratio_social_pop'] = df['Parc social - Nombre de logements'] / df['Nombre  d\'habitants'] * 1000
    
    # 4. Indice de vétusté (âge corrigé par les rénovations)
    if 'Parc social - Âge moyen du parc  (en années)' in df.columns:
        df['indice_vetuste'] = df['Parc social - Âge moyen du parc  (en années)'] * 0.7
        if 'Construction' in df.columns:
            df['indice_vetuste'] -= df['Construction'] * 0.3
    
    # 5. Score de performance énergétique (inversé)
    if 'Parc social - Taux de logements énergivores (E,F,G)* (en %)' in df.columns:
        df['score_performance'] = 100 - df['Parc social - Taux de logements énergivores (E,F,G)* (en %)']
    
    return df

def normalize_minmax(series):
    """Normalisation min-max d'une série"""
    if series.max() == series.min():
        return pd.Series(0.5, index=series.index)
    return (series - series.min()) / (series.max() - series.min())

def normalize_data(df):
    """Normalise les données pour l'analyse"""
    
    # Liste des colonnes à normaliser (sauf celles déjà normalisées)
    cols_to_normalize = [
        'Densité de population au km²',
        'Taux de chômage au T4 (en %)',
        'Parc social - Loyer moyen (en €/m²/mois)*'
    ]
    
    for col in cols_to_normalize:
        if col in df.columns:
            df[f'{col}_norm'] = normalize_minmax(df[col])
    
    return df

def categorize_data(df):
    """Crée des catégories pour l'analyse"""
    
    # Catégorisation par région
    if 'nom_region' in df.columns:
        df['region_groupe'] = pd.Categorical(df['nom_region'])
    
    # Catégorisation par taille de département
    if 'Nombre  d\'habitants' in df.columns:
        bins = [0, 200000, 500000, 1000000, float('inf')]
        labels = ['Très petit', 'Petit', 'Moyen', 'Grand']
        df['taille_departement'] = pd.cut(df['Nombre  d\'habitants'], bins=bins, labels=labels)
    
    # Catégorisation par niveau de pauvreté
    if 'Taux de pauvreté* (en %)' in df.columns:
        bins = [0, 10, 15, 20, float('inf')]
        labels = ['Faible', 'Modéré', 'Élevé', 'Très élevé']
        df['niveau_pauvrete'] = pd.cut(df['Taux de pauvreté* (en %)'], bins=bins, labels=labels)
    
    return df

def get_data_quality_report(df):
    """Génère un rapport de qualité des données"""
    report = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_values': df.isnull().sum().sum(),
        'missing_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
        'duplicate_rows': df.duplicated().sum(),
        'data_types': df.dtypes.value_counts().to_dict(),
        'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
        'categorical_columns': len(df.select_dtypes(include=[object]).columns)
    }
    
    # Statistiques par colonne
    column_stats = {}
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            column_stats[col] = {
                'type': 'numeric',
                'min': df[col].min(),
                'max': df[col].max(),
                'mean': df[col].mean(),
                'median': df[col].median(),
                'std': df[col].std(),
                'missing': df[col].isnull().sum()
            }
        else:
            column_stats[col] = {
                'type': 'categorical',
                'unique_values': df[col].nunique(),
                'most_common': df[col].mode().iloc[0] if not df[col].mode().empty else None,
                'missing': df[col].isnull().sum()
            }
    
    report['column_details'] = column_stats
    
    return report