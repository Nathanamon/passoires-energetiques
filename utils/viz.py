import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import numpy as np

def create_metric_card(title, value, description="", color="normal"):
    """
    Crée une carte de métrique stylisée
    """
    colors = {
        "success": "#10B981",
        "warning": "#F59E0B",
        "danger": "#EF4444",
        "info": "#3B82F6",
        "normal": "#6B7280"
    }
    
    color_hex = colors.get(color, colors["normal"])
    
    html = f"""
    <div style="
        background: linear-gradient(135deg, #F8FAFC 0%, #FFFFFF 100%);
        border-radius: 10px;
        padding: 20px;
        border-left: 5px solid {color_hex};
        margin-bottom: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    ">
        <div style="font-size: 0.9rem; color: #6B7280; font-weight: 600;">
            {title}
        </div>
        <div style="font-size: 2rem; font-weight: 700; color: #1F2937; margin: 10px 0;">
            {value}
        </div>
        <div style="font-size: 0.8rem; color: #6B7280;">
            {description}
        </div>
    </div>
    """
    
    st.markdown(html, unsafe_allow_html=True)

def create_distribution_chart(data, column, title="Distribution"):
    """
    Crée un graphique de distribution
    """
    fig = px.histogram(
        data,
        x=column,
        nbins=30,
        title=title,
        color_discrete_sequence=['#3B82F6'],
        opacity=0.8
    )
    
    fig.update_layout(
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12),
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='#E5E7EB',
        title_font=dict(size=14)
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor='#E5E7EB',
        title_font=dict(size=14)
    )
    
    return fig

def create_map(data, lat_col='latitude', lon_col='longitude', 
               size_col=None, color_col=None, hover_cols=None):
    """
    Crée une carte interactive
    """
    if size_col:
        size = data[size_col]
        size_norm = (size - size.min()) / (size.max() - size.min())
        size_scaled = size_norm * 50 + 10
    else:
        size_scaled = 10
    
    if color_col:
        color = data[color_col]
    else:
        color = None
    
    fig = px.scatter_mapbox(
        data,
        lat=lat_col,
        lon=lon_col,
        size=size_scaled if size_col else None,
        color=color,
        hover_name='nom_departement',
        hover_data=hover_cols if hover_cols else None,
        zoom=5,
        height=600,
        title="Carte des départements",
        color_continuous_scale=px.colors.sequential.Reds if color_col else None
    )
    
    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r":0,"t":30,"l":0,"b":0},
        hovermode='closest'
    )
    
    return fig

def create_gauge_chart(value, title, max_value=100, threshold=70, reverse=False):
    """
    Crée un graphique jauge (gauge chart)
    """
    if reverse:
        # Pour les indicateurs où une valeur basse est meilleure
        normalized_value = (max_value - value) / max_value * 100
    else:
        normalized_value = value / max_value * 100
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [0, max_value]},
            'bar': {'color': "#3B82F6"},
            'steps': [
                {'range': [0, threshold], 'color': "#10B981"},
                {'range': [threshold, max_value], 'color': "#EF4444"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': threshold
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(size=14)
    )
    
    return fig

def create_radar_chart(values, categories, title="Radar Chart"):
    """
    Crée un graphique radar
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name=title,
        line_color='#3B82F6',
        fillcolor='rgba(59, 130, 246, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(values) * 1.2]
            )),
        showlegend=False,
        title=title,
        height=400
    )
    
    return fig

def create_timeline_chart(data, date_col, value_col, group_col=None, title="Évolution temporelle"):
    """
    Crée un graphique d'évolution temporelle
    """
    if group_col:
        fig = px.line(
            data,
            x=date_col,
            y=value_col,
            color=group_col,
            title=title,
            markers=True
        )
    else:
        fig = px.line(
            data,
            x=date_col,
            y=value_col,
            title=title,
            markers=True
        )
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=value_col,
        hovermode="x unified",
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def create_correlation_heatmap(data, columns, title="Matrice de corrélation"):
    """
    Crée une heatmap de corrélation
    """
    corr_matrix = data[columns].corr().round(2)
    
    fig = px.imshow(
        corr_matrix,
        text_auto=True,
        color_continuous_scale='RdBu_r',
        title=title,
        aspect="auto",
        labels=dict(color="Corrélation")
    )
    
    fig.update_layout(
        height=500,
        xaxis_title="",
        yaxis_title="",
        coloraxis_colorbar=dict(
            title="Corrélation",
            tickvals=[-1, -0.5, 0, 0.5, 1]
        )
    )
    
    return fig

def create_box_plot(data, x_col, y_col, title="Distribution par catégorie"):
    """
    Crée un box plot
    """
    fig = px.box(
        data,
        x=x_col,
        y=y_col,
        title=title,
        color=x_col,
        points="all"
    )
    
    fig.update_layout(
        xaxis_title=x_col,
        yaxis_title=y_col,
        showlegend=False,
        boxmode='group'
    )
    
    return fig

def create_sunburst_chart(data, path, values, title="Hiérarchie des données"):
    """
    Crée un graphique sunburst
    """
    fig = px.sunburst(
        data,
        path=path,
        values=values,
        title=title,
        color=values,
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(
        height=600,
        margin=dict(t=30, l=0, r=0, b=0)
    )
    
    return fig

def create_bar_chart_ranking(data, x_col, y_col, title="Classement", orientation='v'):
    """
    Crée un graphique en barres pour le classement
    """
    if orientation == 'h':
        fig = px.bar(
            data,
            x=x_col,
            y=y_col,
            orientation='h',
            title=title,
            color=x_col,
            color_continuous_scale='Reds',
            text=x_col
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    else:
        fig = px.bar(
            data,
            x=x_col,
            y=y_col,
            title=title,
            color=y_col,
            color_continuous_scale='Reds',
            text=y_col
        )
        fig.update_layout(xaxis={'categoryorder': 'total descending'})
    
    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    
    return fig

def create_scatter_matrix(data, dimensions, color_col=None, title="Matrice de dispersion"):
    """
    Crée une matrice de dispersion
    """
    fig = px.scatter_matrix(
        data,
        dimensions=dimensions,
        color=color_col,
        title=title,
        opacity=0.7
    )
    
    fig.update_layout(
        height=800,
        showlegend=True if color_col else False
    )
    
    return fig