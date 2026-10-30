"""Régressions liées au filtrage, au téléchargement et aux callbacks allégés."""
import io
import pandas as pd
import pytest
import app as web


def test_filter_excludes_c_and_preserves_shared_dataset():
    source = web.dataset()
    result = web.filtered(['38', '42', '69'], list('ABDEFG'), [0, 1000])
    assert not result.etiquette_dpe.eq('C').any()
    assert len(result) < len(web.filtered(['38', '42', '69'], list('ABCDEFG'), [0, 1000]))
    assert source.etiquette_dpe.eq('C').any()


def test_csv_download_matches_filtered_rows_and_columns():
    response = web.server.test_client().get('/api/export.csv?departments=69&labels=A,B&min_surface=0&max_surface=1000')
    assert response.status_code == 200
    assert 'attachment' in response.headers['Content-Disposition']
    assert response.data.startswith(b'\xef\xbb\xbf')
    actual = pd.read_csv(io.BytesIO(response.data), dtype={'code_departement_ban': str})
    expected = web.filtered(['69'], ['A', 'B'], [0, 1000])
    assert list(actual.columns) == list(expected.columns)
    assert len(actual) == len(expected)
    assert set(actual.etiquette_dpe) <= {'A', 'B'}
    assert set(actual.code_departement_ban) <= {'69'}


def test_csv_empty_filters_produce_headers_only():
    response = web.server.test_client().get('/api/export.csv?departments=&labels=')
    assert response.status_code == 200
    assert pd.read_csv(io.BytesIO(response.data)).empty


@pytest.mark.parametrize('query', ['min_surface=nan', 'max_surface=inf',
                                  'min_surface=100&max_surface=10', 'labels=X', 'departments=99'])
def test_csv_invalid_filters(query):
    assert web.server.test_client().get('/api/export.csv?' + query).status_code == 400


def test_chart_callback_never_builds_map(monkeypatch):
    def fail(*args):
        raise AssertionError('Une carte ne doit pas être reconstruite lors du choix du graphique.')
    monkeypatch.setattr(web, 'exportable_map', fail)
    for chart in web.CHARTS:
        assert web.update_chart(['69'], ['A'], [0, 1000], chart).data
