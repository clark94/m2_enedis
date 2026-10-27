"""Application pédagogique Dash : exploration, carte, prédiction et maintenance locale."""
import os
import json
import subprocess
import sys
from dash import Dash, html, dcc, Input, Output, State, ALL, ctx, dash_table
from flask import request, jsonify
import pandas as pd
import plotly.graph_objects as go
from src.service import dataset, predict, metrics, ROOT, LOCK
from src.config import FEATURES
from src.charts import dpe_bar, heating_histogram, heating_box, surface_scatter
from src.mapping import valid_coordinates, build_map, map_html

app=Dash(__name__, title='GreenTech — DPE', suppress_callback_exceptions=True)
server=app.server
CHARTS={'Barres':dpe_bar,'Histogramme':heating_histogram,'Boîte à moustaches':heating_box,'Nuage de points':surface_scatter}


DPE_COLORS = {'A':'#188450','B':'#45a65a','C':'#91b744','D':'#e4bf32',
              'E':'#e89332','F':'#d65d3d','G':'#b52b3d'}
CARD_STYLE = {'background':'#fff','border':'1px solid #dce7e3','borderRadius':'14px',
              'padding':'22px','boxShadow':'0 3px 14px rgba(20,60,45,.05)'}
GRID_STYLE = {'display':'grid','gridTemplateColumns':'repeat(auto-fit,minmax(220px,1fr))',
              'gap':'16px','margin':'20px 0'}

def number_fr(value, decimals=0):
    return f'{float(value):,.{decimals}f}'.replace(',', ' ').replace('.', ',')

def stat_card(label, value, note='', color='#205e50'):
    return html.Div([
        html.P(label,style={'margin':'0 0 10px','color':'#52645d','fontSize':'14px'}),
        html.Div(value,style={'fontSize':'32px','fontWeight':'700','color':color}),
        html.P(note,style={'fontSize':'13px','color':'#52645d','marginBottom':0})
    ],style=CARD_STYLE)

def technical_details(data):
    return html.Details([html.Summary('Détails techniques (JSON)',style={'cursor':'pointer','fontWeight':600}),
        html.Pre(json.dumps(data,indent=2,ensure_ascii=False),
                 style={'overflowX':'auto','fontSize':'12px','maxHeight':'400px','whiteSpace':'pre-wrap'})],
        style={**CARD_STYLE,'margin':'20px 0'})

def prediction_dashboard(result):
    letter = result['etiquette_dpe']
    probabilities = result['probabilites']
    classes = list('ABCDEFG')
    values = [float(probabilities.get(c,0)) for c in classes]
    figure = go.Figure(go.Bar(
        x=values,y=classes,orientation='h',
        marker_color=[DPE_COLORS[c] for c in classes],
        text=[number_fr(v*100,1)+' %' for v in values],textposition='outside',
        cliponaxis=False,hovertemplate='Classe %{y} : %{x:.1%}<extra></extra>'))
    figure.update_layout(template='plotly_white',height=370,margin=dict(l=35,r=65,t=20,b=45),
        xaxis=dict(range=[0,1.12],tickvals=[0,.25,.5,.75,1],tickformat='.0%',title='Probabilité estimée'),
        yaxis=dict(autorange='reversed',title='Classe DPE'),showlegend=False,
        font=dict(family='Arial, sans-serif'),paper_bgcolor='white',bargap=.28)
    return html.Div([
        html.H3('Résultat de l’estimation'),
        html.Div([
            stat_card('Classe DPE estimée',letter,'Classe la plus probable selon le modèle',DPE_COLORS.get(letter,'#205e50')),
            stat_card('Probabilité attribuée à cette classe',number_fr(float(probabilities[letter])*100,1)+' %',
                      'Probabilité non calibrée ; aucune fiabilité garantie.'),
            stat_card('Consommation de chauffage estimée',number_fr(result['conso_chauffage_ef']),
                      'Énergie finale · unité de la source à confirmer ; aucune conversion appliquée.')
        ],style=GRID_STYLE),
        html.Div([html.H4('Répartition des probabilités A–G'),
            dcc.Graph(figure=figure,config={'displaylogo':False,'toImageButtonOptions':{'format':'png','filename':'probabilites_dpe','scale':2}})
        ],style=CARD_STYLE),
        html.P('Estimation pédagogique, sans valeur de diagnostic officiel. La consommation et la lettre sont deux prédictions distinctes.',
               style={'background':'#edf5f1','padding':'14px','borderRadius':'10px','color':'#294c3d'}),
        technical_details(result)
    ])

def metric_table(headers, rows):
    cell = {'padding':'13px 16px','textAlign':'left','borderBottom':'1px solid #e4ece8','whiteSpace':'nowrap'}
    return html.Div(html.Table([
        html.Thead(html.Tr([html.Th(h,style={**cell,'background':'#edf5f1','color':'#234d3e'}) for h in headers])),
        html.Tbody([html.Tr([html.Td(v,style=cell) for v in row]) for row in rows])
    ],style={'width':'100%','borderCollapse':'collapse','fontSize':'14px'}),style={'overflowX':'auto'})

def model_dashboard():
    data = metrics()
    classification = data.get('classification',{})
    regression = data.get('regression',{})
    labels = [('baseline_logistic_regression','Régression logistique'),('selected_random_forest','Random Forest')]
    class_rows = []
    for key,label in labels:
        scores = classification.get(key,{})
        if scores:
            class_rows.append([label]+[number_fr(scores[k]*100,1)+' %' for k in ['accuracy','precision','recall','f1']]+[number_fr(scores['roc_auc'],3)])
    reg_rows = []
    for key,label in [('baseline_linear_regression','Régression linéaire'),('selected_random_forest','Random Forest')]:
        scores = regression.get(key,{})
        if scores:
            reg_rows.append([label,number_fr(scores['rmse'],1),number_fr(scores['mae'],1),number_fr(scores['r2'],3)])
    matrices = []
    classes = data.get('classes',list('ABCDEFG'))
    for key,label in labels:
        matrix = classification.get(key,{}).get('confusion_matrix')
        if matrix is None:
            continue
        figure = go.Figure(go.Heatmap(z=matrix,x=classes,y=classes,colorscale='Greens',
            text=matrix,texttemplate='%{text}',colorbar=dict(title='Effectif'),
            hovertemplate='Classe réelle : %{y}<br>Classe prédite : %{x}<br>Effectif : %{z}<extra></extra>'))
        figure.update_layout(template='plotly_white',height=430,margin=dict(l=60,r=30,t=20,b=60),
                              xaxis_title='Classe prédite',yaxis_title='Classe réelle',yaxis_autorange='reversed')
        matrices.append(html.Div([html.H4(label),dcc.Graph(figure=figure,config={'displaylogo':False})],style=CARD_STYLE))
    rf = classification.get('selected_random_forest',{})
    rfr = regression.get('selected_random_forest',{})
    cards = [stat_card('Diagnostics du jeu d’évaluation et d’apprentissage',number_fr(data.get('dataset',{}).get('rows',0)),
                       'Instantané associé aux métriques ; les données explorées peuvent avoir été actualisées.')]
    if 'accuracy' in rf:
        cards.append(stat_card('Random Forest · lettres exactes',number_fr(rf['accuracy']*100,1)+' %','Score sur le jeu de test.'))
    if 'r2' in rfr:
        cards.append(stat_card('Random Forest · R²',number_fr(rfr['r2'],3),'Le R² n’est pas un taux de prédictions exactes.'))
    enrichment = data.get('enrichment',{})
    pop_rows = [[d['code_departement_ban'],number_fr(d['population_departement']),number_fr(d['communes'])]
                for d in enrichment.get('departements',[])]
    return html.Div([
        html.Div(cards,style=GRID_STYLE),
        html.Div([html.H3('Classification · prédire la lettre DPE'),
            metric_table(['Modèle','Accuracy','Précision macro','Rappel macro','F1 macro','AUC macro'],class_rows),
            html.P('Accuracy : proportion de lettres exactement prédites. Les métriques macro donnent le même poids à chaque classe. L’AUC mesure la séparation des classes, pas la calibration des probabilités.')],style={**CARD_STYLE,'marginBottom':'20px'}),
        html.H3('Matrices de confusion'),
        html.P('La diagonale compte les prédictions correctes ; les autres cases montrent les confusions.'),
        html.Div(matrices,style={'display':'grid','gridTemplateColumns':'repeat(auto-fit,minmax(310px,1fr))','gap':'16px'}),
        html.Div([html.H3('Régression · estimer la consommation de chauffage'),
            metric_table(['Modèle','RMSE ↓','MAE ↓','R² ↑'],reg_rows),
            html.P('RMSE et MAE : plus bas signifie moins d’erreur. R² : plus élevé signifie une meilleure performance relative à la moyenne. Les erreurs utilisent l’unité numérique de la source, à confirmer.'),
            html.P('Une RMSE nettement supérieure à la MAE signale de grosses erreurs sur certains cas. Ces scores globaux ne garantissent pas une précision identique pour tous les logements.')],style={**CARD_STYLE,'marginTop':'20px'}),
        html.Div([html.H3('Enrichissement OpenData · population départementale'),
            metric_table(['Département','Population agrégée','Communes'],pop_rows),
            html.P('Source : API Découpage administratif de l’État. Variable de contexte commune aux logements du même département ; aucun lien causal ni gain prédictif démontré.'),
            html.P('Récupération : '+str(enrichment.get('retrieved_at','non renseignée'))+' · millésime de population non garanti.')],style={**CARD_STYLE,'marginTop':'20px'}),
        technical_details(data)
    ])


def layout():
    df=dataset()
    controls=[]
    for col in FEATURES:
        values=df[col].dropna()
        if col in ['hauteur_sous_plafond','surface_habitable_logement','annee_construction']:
            component=dcc.Input(id={'type':'feature','index':col},type='number',value=float(values.median()))
        else:
            options=sorted(values.astype(str).unique())
            component=dcc.Dropdown(options, options[0],id={'type':'feature','index':col},clearable=False)
        controls.append(html.Div([html.Label(col.replace('_',' ')),component],className='field'))
    return html.Main([
        html.Header([html.Img(src='/assets/greentech_logo.svg',height=48),html.H1('GreenTech Solutions'),html.P('Explorer les DPE et estimer la performance énergétique des logements')]),
        dcc.Tabs([
            dcc.Tab(label='📚 Contexte',children=[html.H2('Données ADEME : logements neufs et existants'),html.P('Échantillon Rhône, Isère, Loire. Estimations pédagogiques, sans valeur de diagnostic officiel.'),html.P(f'{len(df):,} observations. Les consommations portent sur le chauffage en énergie finale, pas uniquement l’électricité.'),html.A('Source ADEME',href='https://data.ademe.fr/'),html.H3('Qualité des données'),dash_table.DataTable(data=[{'variable':c,'manquants_pct':round(df[c].isna().mean()*100,2)} for c in df.columns],page_size=12)]),
            dcc.Tab(label='📊 Exploration et carte',children=[html.H2('Filtres partagés'),dcc.Dropdown(sorted(df.code_departement_ban.unique()),sorted(df.code_departement_ban.unique()),multi=True,id='departments'),dcc.Checklist(list('ABCDEFG'),list('ABCDEFG'),id='labels',inline=True),html.Label('Surface habitable (m²)'),dcc.RangeSlider(0,1000,10,value=[0,1000],marks={n:str(n) for n in range(0,1001,100)},id='surface',tooltip={'placement':'bottom','always_visible':False}),dcc.RadioItems(list(CHARTS),'Barres',id='chart',inline=True),html.Div(id='kpis'),dcc.Graph(id='graph',config={'displaylogo':False,'toImageButtonOptions':{'format':'png','filename':'graphique_dpe','scale':2}}),html.Button('Télécharger le graphique en PNG',id='graph-png'),html.Span(id='graph-png-status',role='status'),html.Button('Exporter les données CSV',id='csv'),dcc.Download(id='download'),html.H3('Carte interactive'),html.P('Au maximum 2 000 points échantillonnés pour préserver la fluidité.'),html.Div(id='geo-status'),html.Iframe(id='map',style={'width':'100%','height':'600px','border':0}),dash_table.DataTable(id='table',page_size=10,style_table={'overflowX':'auto'})]),
            dcc.Tab(label='🏠 Prédiction A–G',children=[html.H2('Caractéristiques du logement'),html.Div(controls,className='form'),html.Button('Prédire',id='predict'),html.Div(id='prediction',role='status'),html.P('E est une classe énergivore ; le terme réglementaire « passoire énergétique » concerne F et G.')]),
            dcc.Tab(label='🧪 Modèles et méthode',children=[html.H2('Comparaison des modèles'),html.P('Split 70/30 stratifié pour la classification, preprocessing appris sur train uniquement. Cibles et consommations exclues des prédicteurs.'),model_dashboard(),html.A('API : schéma et exemple',href='/api/schema')]),
            dcc.Tab(label='⚙ Maintenance',children=[html.H2('Actualisation et réentraînement'),html.P('Ces opérations sont disponibles uniquement en mode maintenance local : définir ENABLE_MAINTENANCE=1. Le serveur public doit laisser ce mode désactivé.'),html.Label('DPE reçus depuis (AAAA-MM-JJ)'),dcc.Input(id='since',type='text',value='2026-01-01'),html.Button('Actualiser via ADEME',id='refresh'),html.Button('Réentraîner sur les données actuelles',id='train'),dcc.Loading(html.Div(id='maintenance-result',role='status')),html.P('Après actualisation, recharger la page. Le réentraînement complet peut durer plusieurs minutes.')])
        ]),html.Footer('M2 SISE • Données ouvertes ADEME • Prototype pédagogique')])
app.layout=layout


def exportable_map(sample):
    """Ajoute un export de la vue courante, marqueurs et attribution inclus.

    html2canvas est chargé à la demande. Internet et les autorisations CORS
    du fournisseur de tuiles sont nécessaires ; une erreur reste visible.
    """
    from branca.element import Element
    import folium
    carte = build_map(sample)
    # Les images doivent être chargées avec CORS avant toute capture canvas.
    for layer in carte._children.values():
        if isinstance(layer, folium.raster_layers.TileLayer):
            layer.options['crossOrigin'] = True
    carte.get_root().script.add_child(Element(r"""
    window.addEventListener('load', function () {
        const map = MAP_VARIABLE;
        const ExportControl = L.Control.extend({
            options: {position: 'topleft'},
            onAdd: function () {
                const box = L.DomUtil.create('div', 'leaflet-bar png-export-control');
                box.style.cssText = 'background:white;padding:8px;max-width:240px';
                const button = document.createElement('button');
                button.type = 'button';
                button.textContent = 'Télécharger la carte en PNG';
                button.style.cssText = 'cursor:pointer;padding:7px;color:white;background:#23796c;border:0;border-radius:4px';
                const status = document.createElement('div');
                status.setAttribute('role', 'status');
                status.style.cssText = 'font-size:12px;white-space:normal';
                box.append(button, status);
                L.DomEvent.disableClickPropagation(box);
                L.DomEvent.disableScrollPropagation(box);
                button.onclick = async function () {
                    button.disabled = true;
                    status.textContent = 'Préparation du PNG…';
                    try {
                        if (!window.html2canvas) {
                            await new Promise((resolve, reject) => {
                                const script = document.createElement('script');
                                script.src = 'https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js';
                                script.onload = resolve;
                                script.onerror = () => reject(new Error('Chargement de l’outil PNG impossible. Vérifiez Internet.'));
                                document.head.appendChild(script);
                            });
                        }
                        const node = map.getContainer();
                        const images = Array.from(node.querySelectorAll('img'));
                        await Promise.all(images.map(img => new Promise((resolve, reject) => {
                            if (img.complete) return img.naturalWidth ? resolve() : reject(new Error('Une tuile est absente. Réessayez après chargement de la carte.'));
                            const timer = setTimeout(() => reject(new Error('La carte met trop de temps à charger.')), 15000);
                            img.addEventListener('load', () => {clearTimeout(timer);resolve();}, {once:true});
                            img.addEventListener('error', () => {clearTimeout(timer);reject(new Error('Une tuile ne peut pas être chargée.'));}, {once:true});
                        })));
                        await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
                        const canvas = await html2canvas(node, {
                            useCORS:true, allowTaint:false, backgroundColor:'#ffffff',
                            scale:2, logging:false, imageTimeout:15000,
                            ignoreElements: el => el.classList && el.classList.contains('png-export-control')
                        });
                        const blob = await new Promise(resolve => canvas.toBlob(resolve, 'image/png'));
                        if (!blob) throw new Error('La création du fichier PNG a échoué.');
                        const url = URL.createObjectURL(blob);
                        const link = document.createElement('a');
                        link.href = url;
                        link.download = 'carte_dpe.png';
                        document.body.appendChild(link);
                        link.click();link.remove();
                        setTimeout(() => URL.revokeObjectURL(url), 60000);
                        status.textContent = 'PNG généré. Vérifiez vos téléchargements.';
                    } catch (error) {
                        status.textContent = 'Export impossible : ' + error.message;
                    } finally {button.disabled = false;}
                };
                return box;
            }
        });
        map.addControl(new ExportControl());
    });
    """.replace('MAP_VARIABLE', carte.get_name())))
    return map_html(carte)

# Plotly est déjà fourni par dcc.Graph : aucun ajout à requirements.txt.
app.clientside_callback(
    """async function(clicks) {
        if (!clicks) return window.dash_clientside.no_update;
        const root = document.getElementById('graph');
        const graph = root && root.querySelector('.js-plotly-plot');
        if (!graph || !window.Plotly) return ' Graphique indisponible.';
        try {
            await window.Plotly.downloadImage(graph, {
                format:'png', filename:'graphique_dpe', scale:2
            });
            return ' PNG généré.';
        } catch (error) {return ' Échec de l’export : ' + error.message;}
    }""",
    Output('graph-png-status','children'), Input('graph-png','n_clicks'),
    prevent_initial_call=True
)

def filtered(deps,labels,surface):
    df=dataset()
    return df[df.code_departement_ban.isin(deps or []) & df.etiquette_dpe.isin(labels or []) & df.surface_habitable_logement.between(*(surface or [0,1000]))]

@app.callback(Output('graph','figure'),Output('kpis','children'),Output('map','srcDoc'),Output('table','data'),Output('table','columns'),Output('geo-status','children'),Input('departments','value'),Input('labels','value'),Input('surface','value'),Input('chart','value'))
def explore(deps,labels,surface,chart):
    df=filtered(deps,labels,surface)
    cols=['etiquette_dpe','nom_commune_ban','surface_habitable_logement','conso_chauffage_ef']
    if df.empty:
        return go.Figure(), 'Aucune donnée', '', [], [{'name':c,'id':c} for c in cols],''
    geo=valid_coordinates(df)
    sample=geo.sample(min(2000,len(geo)),random_state=42)
    document=exportable_map(sample) if len(sample) else '<p>Aucune coordonnée valide.</p>'
    kpi=f'{len(df):,} logements | F/G : {df.etiquette_dpe.isin(["F","G"]).mean():.1%} | Surface médiane : {df.surface_habitable_logement.median():.1f} m² | Chauffage médian : {df.conso_chauffage_ef.median():.0f}'
    return CHARTS[chart](df),kpi,document,df[cols].head(1000).astype(object).where(pd.notna(df[cols].head(1000)),None).to_dict('records'),[{'name':c,'id':c} for c in cols],f'{len(df)-len(geo)} coordonnées absentes ou hors fenêtre régionale exclues ; {len(sample)} points affichés.'

@app.callback(Output('download','data'),Input('csv','n_clicks'),State('departments','value'),State('labels','value'),State('surface','value'),prevent_initial_call=True)
def export(_,deps,labels,surface):
    return dcc.send_data_frame(filtered(deps,labels,surface).to_csv,'dpe_selection.csv',index=False)

@app.callback(Output('prediction','children'),Input('predict','n_clicks'),State({'type':'feature','index':ALL},'value'),State({'type':'feature','index':ALL},'id'),prevent_initial_call=True)
def estimate(_,values,ids):
    try: return prediction_dashboard(predict({i['index']:v for i,v in zip(ids,values)}))
    except (ValueError,TypeError) as exc: return 'Entrée invalide : '+str(exc)

def maintenance_feedback(success, action, details):
    title = (action+' terminé avec succès.') if success else (action+' non terminé.')
    color = '#205e50' if success else '#9a382d'
    note = ('Rechargez la page pour consulter les données et métriques à jour.' if success
            else 'Consultez les détails techniques avant de relancer l’opération.')
    return html.Div([
        html.Div([html.H3(title,style={'marginTop':0,'color':color}),html.P(note)],
                 style={**CARD_STYLE,'borderLeft':'5px solid '+color}),
        html.Details([html.Summary('Voir les détails techniques',style={'cursor':'pointer','fontWeight':600}),
            html.Pre(details or 'Aucun journal supplémentaire.',style={'whiteSpace':'pre-wrap','overflowWrap':'anywhere',
                'maxHeight':'350px','overflowY':'auto','fontSize':'12px'})],
            style={**CARD_STYLE,'marginTop':'12px'})
    ],style={'marginTop':'20px'})

@app.callback(Output('maintenance-result','children'),Input('refresh','n_clicks'),Input('train','n_clicks'),State('since','value'),prevent_initial_call=True,running=[(Output('refresh','disabled'),True,False),(Output('train','disabled'),True,False)])
def maintain(_,__,since):
    if os.getenv('ENABLE_MAINTENANCE')!='1': return 'Mode maintenance désactivé. Voir la documentation technique.'
    if not LOCK.acquire(blocking=False): return 'Une opération est déjà en cours.'
    action = 'Actualisation des données' if ctx.triggered_id=='refresh' else 'Réentraînement des modèles'
    try:
        command=[sys.executable,str(ROOT/'scripts/refresh_data.py'),'--since',since] if ctx.triggered_id=='refresh' else [sys.executable,str(ROOT/'scripts/train_models.py'),'--quick']
        result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,timeout=1800)
        return maintenance_feedback(result.returncode==0,action,result.stdout+result.stderr)
    except subprocess.TimeoutExpired:
        return maintenance_feedback(False,action,'Le délai maximal de 30 minutes a été dépassé. Vérifiez les journaux et les fichiers avant de relancer.')
    except Exception as exc: return maintenance_feedback(False,action,str(exc))
    finally: LOCK.release()

@server.get('/health')
def health(): return jsonify(status='ok')

@server.get('/api/schema')
def schema():
    df=dataset()
    return jsonify(method='POST',path='/api/predict',body={c:(float(df[c].dropna().median()) if c in ['hauteur_sous_plafond','surface_habitable_logement','annee_construction'] else str(df[c].dropna().iloc[0])) for c in FEATURES},targets=['etiquette_dpe','conso_chauffage_ef'])

@server.post('/api/predict')
def api_predict():
    body=request.get_json(silent=True)
    if not isinstance(body,dict): return jsonify(error='Un objet JSON est requis.'),400
    try: return jsonify(predict(body))
    except (ValueError,TypeError) as exc: return jsonify(error=str(exc)),400

if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.getenv('PORT','8050')),debug=False)
