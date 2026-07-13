
const KC_CHAR = {
  KC_A:'a',KC_B:'b',KC_C:'c',KC_D:'d',KC_E:'e',KC_F:'f',KC_G:'g',KC_H:'h',
  KC_I:'i',KC_J:'j',KC_K:'k',KC_L:'l',KC_M:'m',KC_N:'n',KC_O:'o',KC_P:'p',
  KC_Q:'q',KC_R:'r',KC_S:'s',KC_T:'t',KC_U:'u',KC_V:'v',KC_W:'w',KC_X:'x',
  KC_Y:'y',KC_Z:'z', KC_SPC:' ', KC_QUOT:"'", KC_COMM:',', KC_DOT:'.', KC_SLSH:'/',
  KC_0:'0',KC_1:'1',KC_2:'2',KC_3:'3',KC_4:'4',KC_5:'5',KC_6:'6',KC_7:'7',KC_8:'8',KC_9:'9',
  KC_GRV:'`',KC_MINS:'-',KC_EQL:'=',KC_LBRC:'[',KC_RBRC:']',KC_BSLS:'\\',KC_SCLN:';',
  KC_EXLM:'!',KC_AT:'@',KC_HASH:'#',KC_DLR:'$',KC_PERC:'%',KC_CIRC:'^',KC_AMPR:'&',KC_ASTR:'*',
  KC_LPRN:'(',KC_RPRN:')',KC_LCBR:'{',KC_RCBR:'}',KC_COLN:':',KC_PLUS:'+',KC_PIPE:'|',KC_TILD:'~',KC_UNDS:'_'
};

const CODE_TO_POS = {
  KeyQ:'L:0:0', KeyW:'L:0:1', KeyE:'L:0:2', KeyR:'L:0:3', KeyT:'L:0:4',
  KeyY:'R:0:0', KeyU:'R:0:1', KeyI:'R:0:2', KeyO:'R:0:3', KeyP:'R:0:4',
  KeyA:'L:1:0', KeyS:'L:1:1', KeyD:'L:1:2', KeyF:'L:1:3', KeyG:'L:1:4',
  KeyH:'R:1:0', KeyJ:'R:1:1', KeyK:'R:1:2', KeyL:'R:1:3', Semicolon:'R:1:4',
  KeyZ:'L:2:0', KeyX:'L:2:1', KeyC:'L:2:2', KeyV:'L:2:3', KeyB:'L:2:4',
  KeyN:'R:2:0', KeyM:'R:2:1', Comma:'R:2:2', Period:'R:2:3', Slash:'R:2:4',
  Space:'LT:1', Backspace:'LT:0', Enter:'LT:2', Tab:'RT:1', Escape:'RT:0'
};

const POS_TO_CODE = (function(){
  var m = {};
  Object.keys(CODE_TO_POS).forEach(function(k){ m[CODE_TO_POS[k]] = k; });
  return m;
})();

const WORDLIST = ["the","of","and","to","in","a","is","that","it","for","you","was","with","on","as","have","be","but","not","this","are","from","or","by","an","they","we","his","her","she","him","all","would","there","their","if","about","out","can","who","get","which","when","what","make","will","up","like","them","could","time","no","just","know","take","into","year","your","good","some","see","other","than","then","now","look","only","come","over","think","also","back","after","use","two","how","our","work","first","well","way","even","new","want","because","any","give","day","most","us","been","here","more","very","where","much","should","home","such","great","before","left","right","down","still","life","world","while","never","under","again","between","both","house","each","made","hand","ask","off","place","girl","large","write","need","side","try","kind","head","mother","father","light","country","thing","answer","school","grow","study","learn","point","city","story","sea","earth","music","color","stand","sun","book","eye","king","wood","song","door","road","river","feet","keep","fall","ship","idea","rock","field","grass","rain","snow","tree","hill","fire","night","morning","winter","summer","spring","month","happy","small","young","children","table","water","money","friend","plant","start","smile","sweet","dream","quiet","quick","brown","jump","fox","lazy","dog"];

let practice = { active:false, text:'', typed:[], pos:0, startMs:0, correct:0, errors:0, finished:false, emul:true, numbers:false, symbols:false, layerDrill:true, armed:false, armedChord:null };
let posToChar = {}, charToPos = {}, charToChord = {};
let _inHighlight = false;

function tapChar(k){
  if(!k || !k.raw) return null;
  var raw = k.raw;
  var m = raw.match(/LT\([^,]+,\s*(\w+)\)/); if(m) return KC_CHAR[m[1]] || null;
  m = raw.match(/^\w+_T\(\s*(\w+)\)$/); if(m) return KC_CHAR[m[1]] || null;
  return KC_CHAR[raw] || null;
}

function parseLayerTap(raw){
  if(!raw) return null;
  var m = raw.match(/LT\s*\(\s*(\w+)\s*,\s*(\w+)\s*\)/);
  if(m) return { layer: m[1], inner: m[2] };
  return null;
}

function buildPosIndex(){
  posToChar = {}; charToPos = {};
  var b = LAYERS[0];
  ['left','right'].forEach(function(side){
    var sd = side === 'left' ? 'L' : 'R';
    b[side].rows.forEach(function(row, r){
      row.forEach(function(k, c){
        var pk = sd + ':' + r + ':' + c;
        var ch = tapChar(k);
        if(ch){ posToChar[pk] = ch; if(!(ch.toLowerCase() in charToPos)) charToPos[ch.toLowerCase()] = pk; }
      });
    });
    (b[side].thumbs || []).forEach(function(k, i){
      var pk = sd + 'T:' + i;
      var ch = tapChar(k);
      if(ch){ posToChar[pk] = ch; if(!(ch.toLowerCase() in charToPos)) charToPos[ch.toLowerCase()] = pk; }
    });
  });
}

function buildChordIndex(){
  charToChord = {};
  var triggerMap = {};
  // Find layer-trigger thumbs on the base layer
  var base = LAYERS[0];
  ['left','right'].forEach(function(side){
    var sd = side === 'left' ? 'L' : 'R';
    (base[side].thumbs || []).forEach(function(k, i){
      var lt = parseLayerTap(k.raw);
      if(lt && (lt.layer === 'LAYER_NUMERAL' || lt.layer === 'LAYER_SYMBOLS')){
        var pk = sd + 'T:' + i;
        triggerMap[lt.layer] = { triggerPos: pk, triggerPhysicalCode: POS_TO_CODE[pk] };
      }
    });
  });
  // Walk numeral/symbols layers and record chord targets
  LAYERS.forEach(function(l){
    if(l.name !== 'LAYER_NUMERAL' && l.name !== 'LAYER_SYMBOLS') return;
    var trig = triggerMap[l.name];
    if(!trig) return;
    ['left','right'].forEach(function(side){
      var sd = side === 'left' ? 'L' : 'R';
      l[side].rows.forEach(function(row, r){
        row.forEach(function(k, c){
          var ch = tapChar(k);
          if(ch && !(ch.toLowerCase() in charToPos)){
            charToChord[ch] = {
              triggerPos: trig.triggerPos,
              targetPos: sd + ':' + r + ':' + c,
              layerIdx: l.index,
              layerName: l.name,
              triggerPhysicalCode: trig.triggerPhysicalCode
            };
          }
        });
      });
      (l[side].thumbs || []).forEach(function(k, i){
        var ch = tapChar(k);
        if(ch && !(ch.toLowerCase() in charToPos)){
          charToChord[ch] = {
            triggerPos: trig.triggerPos,
            targetPos: sd + 'T:' + i,
            layerIdx: l.index,
            layerName: l.name,
            triggerPhysicalCode: trig.triggerPhysicalCode
          };
        }
      });
    });
  });
}

function fingerName(pk){
  if(pk.indexOf('T') >= 0) return (pk[0] === 'L' ? 'left' : 'right') + ' thumb';
  var parts = pk.split(':'); var s = parts[0]; var col = +parts[2];
  var F = { L:['left pinky','left ring','left middle','left index','left index'],
            R:['right index','right index','right middle','right ring','right pinky'] };
  return F[s][col];
}

function generatePrompt(n, numbers, symbols, layerDrill){
  var SYMS_PASSTHROUGH = ['.', ',', ';', ':', '!', '?'];
  var SYMS_DRILL = Object.keys(charToChord).filter(function(c){
    return charToChord[c].layerName === 'LAYER_SYMBOLS';
  });
  var out = [];
  for(var i=0;i<n;i++){
    if(numbers && Math.random() < 0.15){
      var d = 1 + Math.floor(Math.random()*4);
      var lo = d===1 ? 0 : Math.pow(10, d-1);
      var hi = Math.pow(10, d) - 1;
      out.push(String(lo + Math.floor(Math.random()*(hi-lo+1))));
    } else {
      var w = WORDLIST[Math.floor(Math.random()*WORDLIST.length)];
      if(symbols && Math.random() < 0.30){
        var pool = layerDrill ? SYMS_DRILL : SYMS_PASSTHROUGH;
        w += pool[Math.floor(Math.random()*pool.length)];
      }
      out.push(w);
    }
  }
  return out.join(' ');
}

function pickWords(n){ return generatePrompt(n, false, false, false); }

function clearNextKey(){
  document.querySelectorAll('.key.next-key').forEach(function(e){ e.classList.remove('next-key'); });
}

function startPractice(){
  var n = parseInt(document.getElementById('wordCount').value, 10) || 25;
  n = Math.max(5, Math.min(100, n));
  practice.emul = document.getElementById('emulToggle').checked;
  practice.numbers = document.getElementById('numbersToggle') ? document.getElementById('numbersToggle').checked : false;
  practice.symbols = document.getElementById('symbolsToggle') ? document.getElementById('symbolsToggle').checked : false;
  practice.layerDrill = document.getElementById('layerDrillToggle') ? document.getElementById('layerDrillToggle').checked : true;
  practice.text = generatePrompt(n, practice.numbers, practice.symbols, practice.layerDrill);
  practice.typed = []; practice.pos = 0; practice.startMs = 0;
  practice.correct = 0; practice.errors = 0; practice.finished = false;
  practice.active = true; cur = 0;
  ['search','tabs'].forEach(function(id){ var e = document.getElementById(id); if(e) e.style.display = 'none'; });
  document.querySelectorAll('.legend, #info').forEach(function(e){ e.style.display = 'none'; });
  var panel = document.getElementById('practicePanel'); if(panel) panel.hidden = false;
  var res = document.getElementById('results'); if(res) res.hidden = true;
  var s = document.getElementById('search'); if(s){ s.value=''; s.blur(); }
  term = '';
  if(document.activeElement && document.activeElement.blur) document.activeElement.blur();
  var wc = document.getElementById('wordCount'); if(wc) wc.disabled = true;
  var et = document.getElementById('emulToggle'); if(et) et.disabled = true;
  var nt = document.getElementById('numbersToggle'); if(nt) nt.disabled = true;
  var st = document.getElementById('symbolsToggle'); if(st) st.disabled = true;
  var ld = document.getElementById('layerDrillToggle'); if(ld) ld.disabled = true;
  document.getElementById('modeToggle').textContent = '✕ Exit Practice';
  render(); renderPrompt(); highlightNextKey(); updateStats();
}

function restart(){ startPractice(); }

function exitPractice(){
  practice.active = false;
  ['search','tabs'].forEach(function(id){ var e = document.getElementById(id); if(e) e.style.display = ''; });
  var wc = document.getElementById('wordCount'); if(wc) wc.disabled = false;
  var et = document.getElementById('emulToggle'); if(et) et.disabled = false;
  var nt = document.getElementById('numbersToggle'); if(nt) nt.disabled = false;
  var st = document.getElementById('symbolsToggle'); if(st) st.disabled = false;
  var ld = document.getElementById('layerDrillToggle'); if(ld) ld.disabled = false;
  document.querySelectorAll('.legend, #info').forEach(function(e){ e.style.display = ''; });
  var panel = document.getElementById('practicePanel'); if(panel) panel.hidden = true;
  clearNextKey();
  document.getElementById('modeToggle').textContent = '▶ Practice';
  document.getElementById('fingerHint').textContent = 'Press ▶ Practice to begin…';
  cur = 0;
  render();
}

function renderPrompt(){
  var el = document.getElementById('prompt'); var html = '';
  for(var i=0;i<practice.text.length;i++){
    var ch = practice.text[i];
    var cls = 'char';
    if(i < practice.pos){ cls += practice.typed[i].ok ? ' correct' : ' incorrect'; }
    else if(i === practice.pos && !practice.finished){ cls += ' current'; }
    var esc = ch === ' ' ? '&nbsp;' : ch.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
    html += '<span class="' + cls + '">' + esc + '</span>';
  }
  el.innerHTML = html;
}

function highlightNextKey(){
  if(_inHighlight) return;
  _inHighlight = true;
  try {
    clearNextKey();
    if(practice.finished || practice.pos >= practice.text.length){
      document.getElementById('fingerHint').textContent = '';
      return;
    }
    var c = practice.text[practice.pos].toLowerCase();
    var isChord = practice.layerDrill && !(c in charToPos) && (c in charToChord);
    var wantLayer = isChord ? charToChord[c].layerIdx : 0;
    if(cur !== wantLayer){
      cur = wantLayer;
      render();
      // fall through to apply highlights on the now-current layer
    }
    if(isChord){
      var chord = charToChord[c];
      var triggerEl = document.querySelector('[data-pos="' + chord.triggerPos + '"]');
      var targetEl  = document.querySelector('[data-pos="' + chord.targetPos + '"]');
      if(triggerEl) triggerEl.classList.add('next-key');
      if(targetEl){
        targetEl.classList.add('next-key');
        if(practice.armed) targetEl.classList.add('next-target');
      }
      document.getElementById('fingerHint').textContent =
        'Next: ' + fingerName(chord.triggerPos) + ' + ' + fingerName(chord.targetPos);
    } else {
      var pk = charToPos[c];
      if(pk){
        var el = document.querySelector('[data-pos="' + pk + '"]');
        if(el) el.classList.add('next-key');
        document.getElementById('fingerHint').textContent = 'Next: ' + fingerName(pk);
      } else {
        document.getElementById('fingerHint').textContent = 'Next: (direct)';
      }
    }
  } finally {
    _inHighlight = false;
  }
}

function updateStats(){
  var ks = practice.correct + practice.errors;
  var min = practice.startMs ? (Date.now() - practice.startMs) / 60000 : 0;
  var wpm = min > 0 ? Math.round((practice.correct / 5) / min) : 0;
  var acc = ks > 0 ? Math.round(practice.correct / ks * 100) : 100;
  document.getElementById('wpm').textContent = wpm;
  document.getElementById('acc').textContent = acc + '%';
  document.getElementById('progress').textContent = practice.pos + ' / ' + practice.text.length;
}

function finishTest(){
  practice.finished = true;
  updateStats();
  clearNextKey();
  document.getElementById('fingerHint').textContent = '';
  var ks = practice.correct + practice.errors;
  var acc = ks > 0 ? Math.round(practice.correct / ks * 100) : 100;
  var min = practice.startMs ? (Date.now() - practice.startMs) / 60000 : 0;
  var wpm = min > 0 ? Math.round((practice.correct / 5) / min) : 0;
  var res = document.getElementById('results');
  res.hidden = false;
  res.innerHTML = '<h3>✓ Test complete</h3>'
    + '<p>WPM <b>' + wpm + '</b> · Accuracy <b>' + acc + '%</b> '
    + '(' + practice.correct + '/' + ks + ' correct)</p>'
    + '<button id="againBtn" class="results-btn">↻ Try again</button>';
  var again = document.getElementById('againBtn'); if(again) again.onclick = restart;
}

function handleBackspace(){
  if(practice.armed){
    practice.armed = false;
    practice.armedChord = null;
    renderPrompt(); updateStats(); highlightNextKey();
    return;
  }
  if(practice.pos > 0){
    practice.pos--;
    practice.typed.pop();
    renderPrompt(); updateStats(); highlightNextKey();
  }
}

function onKeydown(e){
  if(!practice.active || practice.finished) return;
  if(e.key === 'Backspace'){ e.preventDefault(); handleBackspace(); return; }
  if(e.ctrlKey || e.metaKey || e.altKey) return;

  var target = practice.text[practice.pos].toLowerCase();

  // ── Chord path (layer drill ON and target is a chord char) ──
  if(practice.layerDrill && !(target in charToPos) && target in charToChord){
    var chord = charToChord[target];
    e.preventDefault();
    if(!practice.startMs) practice.startMs = Date.now();

    if(!practice.armed){
      // IDLE: waiting for the layer-trigger thumb
      if(e.code === chord.triggerPhysicalCode){
        practice.armed = true;
        practice.armedChord = chord;
        highlightNextKey();   // re-highlight: target now gets .next-target
      } else {
        // Wrong key while trigger expected → incorrect, advance
        practice.typed.push({ ch: (e.key && e.key.length === 1) ? e.key : e.code, ok: false });
        practice.errors++;
        practice.pos++;
        renderPrompt(); updateStats(); highlightNextKey();
        if(practice.pos >= practice.text.length) finishTest();
      }
    } else {
      // ARMED: waiting for the target key
      var targetCode = POS_TO_CODE[chord.targetPos];
      if(e.code === targetCode){
        practice.typed.push({ ch: target, ok: true });
        practice.correct++;
      } else {
        practice.typed.push({ ch: (e.key && e.key.length === 1) ? e.key : e.code, ok: false });
        practice.errors++;
      }
      practice.armed = false;
      practice.armedChord = null;
      practice.pos++;
      renderPrompt(); updateStats(); highlightNextKey();
      if(practice.pos >= practice.text.length) finishTest();
    }
    return;
  }

  // ── Global Tab guard (non-chord Tab) ──
  if(e.key === 'Tab'){ e.preventDefault(); return; }

  // ── Base / passthrough path (approach A, unchanged) ──
  var pk = CODE_TO_POS[e.code];
  var ch = null;
  var onBase = (target in charToPos);
  if(practice.emul && onBase){
    ch = pk ? posToChar[pk] : null;
  } else {
    ch = (e.key && e.key.length === 1) ? e.key : null;
  }
  if(ch === null) return;
  e.preventDefault();
  if(!practice.startMs) practice.startMs = Date.now();
  var ok = ch.toLowerCase() === target;
  practice.typed.push({ ch: ch, ok: ok });
  if(ok) practice.correct++; else practice.errors++;
  practice.pos++;
  renderPrompt(); updateStats(); highlightNextKey();
  if(practice.pos >= practice.text.length) finishTest();
}

buildPosIndex();
buildChordIndex();
document.getElementById('modeToggle').onclick = function(){ if(practice.active) exitPractice(); else startPractice(); };
document.getElementById('restartBtn').onclick = restart;
document.getElementById('exitBtn').onclick = exitPractice;
document.addEventListener('keydown', onKeydown);
window.addEventListener('paste', function(e){ if(practice.active) e.preventDefault(); });
