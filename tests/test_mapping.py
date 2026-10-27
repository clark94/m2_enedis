import pandas as pd
import pytest
from src.mapping import valid_coordinates, build_map, map_html
from src.data import apply_filters


def test_bad_coordinates_are_excluded():
    df = pd.DataFrame({'latitude': [45.7, -5.98, None, 'oops'], 'longitude': [4.8, 4.8, 4.8, 4.8]})
    assert valid_coordinates(df).index.tolist() == [0]


def test_map_contains_markers_and_escaped_popup():
    df = pd.DataFrame({'latitude': [45.7], 'longitude': [4.8],
                       'nom_commune_ban': ['<script>alert(1)</script>'], 'etiquette_dpe': ['E']})
    html = map_html(build_map(df))
    assert 'L.circleMarker' in html
    assert 'L.markerClusterGroup' in html
    assert 'OpenStreetMap' in html
    assert '&lt;script&gt;' in html
    assert 'map-diagnostic' in html


def test_empty_map_rejected():
    with pytest.raises(ValueError):
        build_map(pd.DataFrame())


def test_empty_selection_means_zero_rows():
    df = pd.DataFrame({'code_departement_ban': ['69', '38']})
    assert apply_filters(df, departments=[]).empty


def test_javascript_data_cannot_close_script_tag():
    df = pd.DataFrame({'latitude': [45.7], 'longitude': [4.8],
        'nom_commune_ban': ['</script><script>alert(1)</script>'], 'etiquette_dpe': ['E']})
    html = map_html(build_map(df))
    assert 'window.initDpeControls(' in html
    assert '</script><script>alert(1)</script>' not in html
    assert 'dpe-panel' in html
