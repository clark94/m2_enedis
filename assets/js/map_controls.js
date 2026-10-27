/* Leaflet controls: works inside the Folium iframe and downloaded HTML. */
window.initDpeControls = function (map, cluster, entries, palette) {
  'use strict';
  const originalBounds = L.latLngBounds(entries.map(e => e.marker.getLatLng()));
  const control = L.control({position: 'topright'});
  control.onAdd = function () {
    const panel = L.DomUtil.create('section', 'dpe-panel');
    panel.setAttribute('aria-label', 'Outils de la carte DPE');
    const heading = document.createElement('strong');
    heading.textContent = 'Explorer les logements';
    panel.appendChild(heading);
    const sub = document.createElement('p');
    sub.textContent = 'Recherche parmi les points affichés';
    panel.appendChild(sub);
    const input = document.createElement('input');
    input.type = 'search'; input.placeholder = 'Rechercher une commune…';
    input.setAttribute('aria-label', 'Commune parmi les points affichés');
    input.setAttribute('list', 'dpe-communes'); panel.appendChild(input);
    const list = document.createElement('datalist'); list.id = 'dpe-communes';
    [...new Set(entries.map(e => e.city).filter(Boolean))].sort().forEach(city => {
      const option = document.createElement('option'); option.value = city; list.appendChild(option);
    }); panel.appendChild(list);
    const actions = document.createElement('div'); actions.className = 'dpe-actions'; panel.appendChild(actions);
    const notice = document.createElement('p'); notice.className = 'dpe-notice';
    notice.setAttribute('role', 'status'); notice.setAttribute('aria-live', 'polite');
    function button(text, action) {
      const b = document.createElement('button'); b.type = 'button'; b.textContent = text;
      b.addEventListener('click', action); actions.appendChild(b); return b;
    }
    const normalize = s => s.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().trim();
    const findCity = () => {
      const query = normalize(input.value);
      if (!query) { notice.textContent = 'Saisissez une commune.'; return; }
      const found = entries.filter(e => cluster.hasLayer(e.marker) && normalize(e.city).includes(query));
      if (!found.length) { notice.textContent = 'Aucun point affiché pour cette commune et ces filtres.'; return; }
      const bounds = L.latLngBounds(found.map(e => e.marker.getLatLng()));
      map.fitBounds(bounds, {padding: [35, 35], maxZoom: 14});
      if (found.length === 1) cluster.zoomToShowLayer(found[0].marker, () => found[0].marker.openPopup());
      notice.textContent = found.length + ' logement(s) trouvé(s) dans l’échantillon.';
    };
    button('Rechercher', findCity);
    button('Recentrer', () => { map.fitBounds(originalBounds, {padding: [30, 30], maxZoom: 14}); notice.textContent = ''; });
    input.addEventListener('keydown', e => { if (e.key === 'Enter') { e.preventDefault(); findCity(); } });
    button('Plein écran', async () => {
      try {
        if (document.fullscreenElement) await document.exitFullscreen();
        else if (document.documentElement.requestFullscreen) await document.documentElement.requestFullscreen();
        else throw new Error('unsupported');
      } catch (_) { notice.textContent = 'Plein écran indisponible ici : ouvrez le HTML téléchargé séparément.'; }
      map.invalidateSize();
    });
    const filter = document.createElement('label'); filter.className = 'dpe-toggle';
    const checkbox = document.createElement('input'); checkbox.type = 'checkbox';
    filter.append(checkbox, document.createTextNode(' E/F/G uniquement sur la carte'));
    panel.appendChild(filter);
    const count = document.createElement('div'); count.className = 'dpe-count'; panel.appendChild(count);
    function updateCount() {
      const active = entries.filter(e => cluster.hasLayer(e.marker));
      const risk = active.filter(e => ['E','F','G'].includes(e.label)).length;
      count.textContent = active.length + ' points • ' + risk + ' classés E/F/G';
    }
    checkbox.addEventListener('change', () => {
      entries.forEach(e => {
        if (!checkbox.checked || ['E','F','G'].includes(e.label)) cluster.addLayer(e.marker);
        else cluster.removeLayer(e.marker);
      }); updateCount(); notice.textContent = '';
    });
    const legend = document.createElement('div'); legend.className = 'dpe-legend';
    Object.keys(palette).forEach(label => {
      const item = document.createElement('span');
      const dot = document.createElement('i'); dot.style.backgroundColor = palette[label];
      item.append(dot, document.createTextNode(label)); legend.appendChild(item);
    }); panel.appendChild(legend); panel.appendChild(notice);
    L.DomEvent.disableClickPropagation(panel); L.DomEvent.disableScrollPropagation(panel);
    updateCount(); return panel;
  };
  control.addTo(map);
  L.control.scale({imperial: false, position: 'bottomleft'}).addTo(map);
  document.addEventListener('fullscreenchange', () => window.setTimeout(() => map.invalidateSize(), 80));
  if (window.ResizeObserver) new ResizeObserver(() => map.invalidateSize()).observe(map.getContainer());
  window.setTimeout(() => map.invalidateSize(), 150);
};
