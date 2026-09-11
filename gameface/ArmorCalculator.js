import { ModelObserver } from "../../libs/model.js";

const WIDTH = 220;
const HEIGHT = 24;
const root = document.getElementById('armor-root');
const line = document.getElementById('armor-line');
const observer = ModelObserver();
let lastPayload = null;

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

function ensureSurface() {
  const scale = gameUiScale();
  const width = Math.ceil(WIDTH * scale);
  const height = Math.ceil(HEIGHT * scale);
  document.documentElement.style.width = WIDTH + 'px';
  document.documentElement.style.height = HEIGHT + 'px';
  document.body.style.width = WIDTH + 'px';
  document.body.style.height = HEIGHT + 'px';
  if (root) {
    root.style.width = WIDTH + 'px';
    root.style.height = HEIGHT + 'px';
  }
  try {
    if (window.viewEnv && typeof viewEnv.resizeViewPx === 'function') {
      viewEnv.resizeViewPx(width, height);
    }
  } catch (e) {}
  callModelCommand('onResized', { width: width, height: height, gameScale: scale });
}

function renderModel(model) {
  if (!root || !line) return;
  const raw = model && model.payload ? String(model.payload) : '';
  if (raw === lastPayload) return;
  lastPayload = raw;

  let data = {};
  try {
    data = JSON.parse(raw || '{}');
  } catch (e) {
    data = {};
  }

  if (!data || data.visible !== true || data.armorEnabled !== true) {
    root.style.visibility = 'hidden';
    line.textContent = '';
    return;
  }

  const fontSize = Math.max(10, num(data.fontSize, 16));
  root.style.visibility = 'visible';
  root.style.color = data.color || '#ffffff';
  root.style.fontSize = fontSize + 'px';
  line.style.fontSize = fontSize + 'px';
  line.textContent = String(data.armorText || '');
}

function refreshGeometry() {
  ensureSurface();
  renderModel(observer.model);
}

engine.whenReady.then(() => {
  ensureSurface();
  observer.onUpdate(renderModel);
  observer.subscribe();
  renderModel(observer.model);
  callModelCommand('onReady', {});

  try { window.engine.on('self.onScaleUpdated', refreshGeometry); } catch (e) {}
  try { window.engine.on('clientResized', refreshGeometry); } catch (e) {}
});
