"""Validation des coordonnées et génération de carte, sans dépendance à Streamlit."""
from html import escape
import json
from pathlib import Path
from branca.element import MacroElement, Template
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from .config import DPE_COLORS


def valid_coordinates(df):
    """Fenêtre de contrôle large autour des départements 38/42/69, pas un contour administratif."""
    out = df.copy()
    for col in ('latitude', 'longitude'):
        out[col] = pd.to_numeric(out[col], errors='coerce')
    return out.loc[out.latitude.between(44, 47) & out.longitude.between(3, 7)].copy()


def build_map(df):
    if df.empty:
        raise ValueError('Aucun point géographique valide.')
    center = [float(df.latitude.median()), float(df.longitude.median())]
    m = folium.Map(location=center, zoom_start=8, tiles=None)
    folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m)
    cluster = MarkerCluster(name='DPE').add_to(m)
    entries = []
    for _, row in df.iterrows():
        label = str(row.get('etiquette_dpe', ''))
        color = DPE_COLORS.get(label, '#2A9D8F')
        popup = '<br>'.join([
            '<b>' + escape(str(row.get('nom_commune_ban', ''))) + '</b>',
            'DPE : ' + escape(label),
            'Surface : ' + escape(str(row.get('surface_habitable_logement', ''))) + ' m²',
            'Source : ' + escape(str(row.get('source_dataset', ''))),
        ])
        marker = folium.CircleMarker([float(row.latitude), float(row.longitude)], radius=5,
            color=color, fill=True, fill_color=color, fill_opacity=.8,
            popup=folium.Popup(popup, max_width=280)).add_to(cluster)
        entries.append({'city': str(row.get('nom_commune_ban', '')), 'label': label, 'marker_name': marker.get_name()})
    assets = Path(__file__).resolve().parents[1] / 'assets'
    m.get_root().header.add_child(folium.Element('<style>' + (assets / 'css/map_controls.css').read_text() + '</style>'))
    m.get_root().header.add_child(folium.Element('<script>' + (assets / 'js/map_controls.js').read_text() + '</script>'))
    def safe_json(value):
        return json.dumps(value, ensure_ascii=True).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    js_entries = ','.join('{city:' + safe_json(e['city']) + ',label:' + safe_json(e['label']) + ',marker:' + e['marker_name'] + '}' for e in entries)
    controls = MacroElement()
    controls._template = Template('{% macro script(this, kwargs) %}window.initDpeControls(' + m.get_name() + ',' + cluster.get_name() + ',[' + js_entries + '],' + safe_json(DPE_COLORS) + ');{% endmacro %}')
    m.add_child(controls)
    if len(df) > 1:
        m.fit_bounds([[float(df.latitude.min()), float(df.longitude.min())],
                      [float(df.latitude.max()), float(df.longitude.max())]])
    return m


def map_html(m):
    html = m.get_root().render()
    # Affiche une explication dans l'iframe si Leaflet n'a pas été chargé par le navigateur.
    diagnostic = '''<div id="map-diagnostic" style="display:none;position:fixed;top:12px;left:12px;z-index:99999;background:white;padding:16px;border:2px solid #d77;font-family:sans-serif">
    La bibliothèque de carte n'a pas chargé. Vérifiez la connexion et les blocages de CDN
    (cdn.jsdelivr.net, unpkg.com). Utilisez le téléchargement HTML ou le mode diagnostic.
    </div><script>window.setTimeout(function(){if(typeof L==='undefined'){
    document.getElementById('map-diagnostic').style.display='block';}},2500);</script>'''
    return html.replace('</body>', diagnostic + '</body>')
