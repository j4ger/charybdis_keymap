let cur = 0, term = '';

function tabs() {
  const el = document.getElementById('tabs');
  el.innerHTML = '';
  LAYERS.forEach((l, i) => {
    const b = document.createElement('button');
    b.className = 'layer-tab' + (i === cur ? ' active' : '');
    b.innerHTML = l.name.replace(/_/g,' ').toUpperCase() + '<span class="idx">[' + l.index + ']</span>';
    b.onclick = () => { if (typeof practice !== 'undefined' && practice.active) return; cur = i; render(); };
    el.appendChild(b);
  });
}

function keyHTML(k, isThumb, posKey) {
  const cls = ['key', k.type];
  if (isThumb) cls.push('thumb');
  if (k.layer) cls.push('layer-trigger');
  if (term) {
    const match = k.label.toLowerCase().includes(term) || (k.sub && k.sub.toLowerCase().includes(term));
    if (match) cls.push('search-match');
    else if (k.type !== 'dead') cls.push('search-dim');
  }
  const sub = k.sub ? '<span class="sub">' + k.sub + '</span>' : '';
  const title = [k.label, k.sub, k.raw].filter(Boolean).join(' · ');
  return '<div class="' + cls.join(' ') + '" title="' + title.replace(/"/g,'&quot;') + '"'
    + (k.layer ? ' data-layer="' + k.layer + '"' : '')
    + (posKey ? ' data-pos="' + posKey + '"' : '')
    + '><span class="label">' + k.label + '</span>' + sub + '</div>';
}

function halfHTML(h, sideLabel, side) {
  let html = '<div class="half"><div class="half-label">' + sideLabel + '</div>';
  h.rows.forEach((row, r) => {
    html += '<div class="row">';
    row.forEach((k, c) => html += keyHTML(k, false, side ? side + ':' + r + ':' + c : undefined));
    html += '</div>';
  });
  if (h.thumbs && h.thumbs.length) {
    html += '<div class="thumb-row">';
    h.thumbs.forEach((k, i) => html += keyHTML(k, true, side ? side + 'T:' + i : undefined));
    html += '</div>';
  }
  return html + '</div>';
}

function render() {
  tabs();
  const l = LAYERS[cur];
  const kb = document.getElementById('kb');
  kb.innerHTML = halfHTML(l.left, '← Left', 'L') + halfHTML(l.right, 'Right →', 'R');
  // Click layer triggers
  kb.querySelectorAll('.key.layer-trigger').forEach(el => {
    el.onclick = () => {
      if (typeof practice !== 'undefined' && practice.active) return;
      const target = el.dataset.layer;
      if (!target) return;
      const idx = LAYERS.findIndex(l => l.name === target);
      if (idx >= 0) { cur = idx; render(); }
    };
  });
  // Info
  document.getElementById('info').innerHTML =
    '<h3>' + l.name.replace(/_/g,' ').toUpperCase() + ' Layer [' + l.index + ']</h3>'
    + '<p>Layer index: <span class="hl">' + l.index + '</span></p>';
  if (typeof practice !== 'undefined' && practice.active) highlightNextKey();
}

document.getElementById('search').addEventListener('input', e => {
  term = e.target.value.toLowerCase().trim();
  render();
});

