import { ModelObserver } from "../../libs/model.js";

const observer = ModelObserver();
const root = document.getElementById('armor-root');
const rows = {
  armor: document.getElementById('armor-line'),
  chance: document.getElementById('chance-line'),
  angle: document.getElementById('angle-line'),
  effpen: document.getElementById('effpen-line'),
  kill: document.getElementById('kill-line'),
  gun: document.getElementById('gun-line')
};
let lastSize = '';

function gameUiScale() {
  try {
    if (window.viewEnv && typeof viewEnv.getScale === 'function') {
      const value = Number(viewEnv.getScale());
      if (!isNaN(value) && value > 0) return value;
    }
  } catch (e) {}
  return 1;
}

function callModelCommand(name, payload) {
  try {
    if (window.model && typeof window.model[name] === 'function') {
      window.model[name](payload);
      return;
    }
  } catch (e) {}
  try {
    if (observer.model && typeof observer.model[name] === 'function') {
      observer.model[name](payload);
    }
  } catch (e) {}
}

function setRow(el, enabled, text) {
  if (!el) return;
  el.textContent = text || '';
  el.classList.toggle('visible', !!enabled);
}

function hideRows() {
  Object.keys(rows).forEach((key) => setRow(rows[key], false, ''));
}

function resizeSurface(fontSize) {
  const visibleRows = root ? root.querySelectorAll('.row.visible').length : 0;
  const logicalWidth = 220;
  const lineHeight = Math.max(18, Math.ceil(fontSize * 1.15));
  const logicalHeight = Math.max(4, visibleRows * lineHeight + 4);
  const scale = gameUiScale();
  const width = Math.ceil(logicalWidth * scale);
  const height = Math.ceil(logicalHeight * scale);
  const key = width + 'x' + height + '@' + scale.toFixed(4);
  if (key === lastSize) return;
  lastSize = key;
  try {
    if (window.viewEnv && viewEnv.resizeViewPx) viewEnv.resizeViewPx(width, height);
  } catch (e) {}
  callModelCommand('onResized', {width: width, height: height, gameScale: scale});
}

function render(model) {
  let data = {};
  try {
    data = JSON.parse((model && model.payload) || '{}');
  } catch (e) {
    data = {};
  }
  if (!root) return;
  if (!data.visible) {
    hideRows();
    root.classList.add('hidden');
    resizeSurface(16);
    return;
  }

  const fontSize = Math.max(10, Number(data.fontSize) || 16);
  root.classList.remove('hidden');
  root.style.fontSize = fontSize + 'px';
  root.style.color = data.color || '#ffffff';

  setRow(rows.armor, data.armorEnabled, data.armorText);
  setRow(rows.chance, data.chanceEnabled, data.chanceText);
  setRow(rows.angle, data.angleEnabled, data.angleText);
  setRow(rows.effpen, data.effPenEnabled, data.effPenText);
  setRow(rows.kill, data.killEnabled, data.killText);
  setRow(rows.gun, data.gunEnabled, data.gunText);
  resizeSurface(fontSize);
}

engine.whenReady.then(() => {
  observer.onUpdate(render);
  observer.subscribe();
  render(observer.model);
  callModelCommand('onReady', {});
});
