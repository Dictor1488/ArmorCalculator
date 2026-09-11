import { ModelObserver } from "../../libs/model.js";

const NS = 'http://www.w3.org/2000/svg';
const WIDTH = 220;
const MIN_HEIGHT = 24;
const svg = document.getElementById('armor-svg');
const observer = ModelObserver();

let lastPayload = null;
let lastSize = null;

function num(value, fallback) {
  value = Number(value);
  return isNaN(value) ? fallback : value;
}

function gameUiScale() {
  try {
    if (window.viewEnv && typeof viewEnv.getScale === 'function') {
      const value = num(viewEnv.getScale(), 1);
      if (value > 0) return value;
    }
  } catch (e) {}
  return 1;
}

function callModelCommand(name, payload) {
  try {
    if (window.model && typeof window.model[name] === 'function') {
      window.model[name](payload || {});
      return;
    }
  } catch (e) {}
  try {
    if (observer.model && typeof observer.model[name] === 'function') {
      observer.model[name](payload || {});
    }
  } catch (e) {}
}

function clearSvg() {
  if (!svg) return;
  while (svg.firstChild) svg.removeChild(svg.firstChild);
}

function el(name, attrs, parent) {
  const node = document.createElementNS(NS, name);
  if (attrs) {
    for (const key in attrs) {
      if (Object.prototype.hasOwnProperty.call(attrs, key)) node.setAttribute(key, attrs[key]);
    }
  }
  (parent || svg).appendChild(node);
  return node;
}

function addDefs() {
  const defs = el('defs');
  const filter = el('filter', { id: 'armorShadow', x: '-40%', y: '-80%', width: '180%', height: '260%' }, defs);
  el('feDropShadow', {
    dx: '0',
    dy: '0',
    stdDeviation: '1.6',
    'flood-color': '#000000',
    'flood-opacity': '1'
  }, filter);
}

function resizeSurface(logicalHeight) {
  logicalHeight = Math.max(MIN_HEIGHT, Math.ceil(logicalHeight));
  const scale = gameUiScale();
  const width = Math.ceil(WIDTH * scale);
  const height = Math.ceil(logicalHeight * scale);
  const key = width + 'x' + height + '@' + scale.toFixed(4);

  if (svg) {
    svg.setAttribute('width', WIDTH);
    svg.setAttribute('height', logicalHeight);
    svg.setAttribute('viewBox', '0 0 ' + WIDTH + ' ' + logicalHeight);
    svg.style.height = logicalHeight + 'px';
  }
  document.documentElement.style.height = logicalHeight + 'px';
  document.body.style.height = logicalHeight + 'px';

  if (key === lastSize) return;
  lastSize = key;

  try {
    if (window.viewEnv && typeof viewEnv.resizeViewPx === 'function') {
      viewEnv.resizeViewPx(width, height);
    }
  } catch (e) {}

  callModelCommand('onResized', {
    width: width,
    height: height,
    gameScale: scale
  });
}

function drawText(text, y, fontSize, color) {
  const t = el('text', {
    x: WIDTH / 2,
    y: y,
    fill: color || '#ffffff',
    'font-size': fontSize,
    'font-family': 'Arial, sans-serif',
    'font-weight': '700',
    'text-anchor': 'middle',
    filter: 'url(#armorShadow)'
  });
  t.textContent = String(text || '');
}

function renderData(data) {
  if (!svg) return;
  clearSvg();

  if (!data || data.visible !== true) {
    resizeSurface(MIN_HEIGHT);
    return;
  }

  addDefs();

  const fontSize = Math.max(10, num(data.fontSize, 16));
  const lineHeight = Math.max(18, Math.ceil(fontSize * 1.2));
  const lines = [];

  if (data.armorEnabled === true) lines.push(data.armorText);
  if (data.chanceEnabled === true) lines.push(data.chanceText);
  if (data.angleEnabled === true) lines.push(data.angleText);
  if (data.effPenEnabled === true) lines.push(data.effPenText);
  if (data.killEnabled === true) lines.push(data.killText);
  if (data.gunEnabled === true) lines.push(data.gunText);

  if (!lines.length) {
    resizeSurface(MIN_HEIGHT);
    return;
  }

  const logicalHeight = Math.max(MIN_HEIGHT, lines.length * lineHeight + 4);
  resizeSurface(logicalHeight);

  const baselineOffset = fontSize * 0.82;
  for (let i = 0; i < lines.length; i += 1) {
    const top = 2 + i * lineHeight;
    drawText(lines[i], top + baselineOffset, fontSize, data.color || '#ffffff');
  }
}

function renderModel(model) {
  const raw = model && model.payload ? String(model.payload) : '';
  if (raw === lastPayload) return;
  lastPayload = raw;

  let data = {};
  try {
    data = JSON.parse(raw || '{}');
  } catch (e) {
    data = {};
  }
  renderData(data);
}

function refreshGeometry() {
  lastSize = null;
  renderModel(observer.model);
}

engine.whenReady.then(() => {
  resizeSurface(MIN_HEIGHT);
  observer.onUpdate(renderModel);
  observer.subscribe();
  renderModel(observer.model);
  callModelCommand('onReady', {});

  if (window.engine) {
    try { window.engine.on('self.onScaleUpdated', refreshGeometry); } catch (e) {}
    try { window.engine.on('clientResized', refreshGeometry); } catch (e) {}
  }
});
