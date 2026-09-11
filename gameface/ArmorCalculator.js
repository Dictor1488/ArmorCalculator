(function () {
  'use strict';

  var root = document.getElementById('armor-root');
  var rows = {
    armor: document.getElementById('armor-line'),
    chance: document.getElementById('chance-line'),
    angle: document.getElementById('angle-line'),
    effpen: document.getElementById('effpen-line'),
    kill: document.getElementById('kill-line'),
    gun: document.getElementById('gun-line')
  };

  var lastPayload = null;
  var lastSize = null;
  var pollTimer = null;

  function num(value, fallback) {
    value = Number(value);
    return isNaN(value) ? fallback : value;
  }

  function gameUiScale() {
    try {
      if (window.viewEnv && typeof viewEnv.getScale === 'function') {
        var value = num(viewEnv.getScale(), 1);
        if (value > 0) return value;
      }
    } catch (e) {}
    return 1;
  }

  function callModelCommand(name, payload) {
    try {
      if (window.model && typeof window.model[name] === 'function') {
        window.model[name](payload || {});
      }
    } catch (e) {}
  }

  function setRow(element, enabled, text) {
    if (!element) return;
    element.textContent = text || '';
    if (enabled) element.classList.add('visible');
    else element.classList.remove('visible');
  }

  function hideRows() {
    for (var key in rows) {
      if (rows.hasOwnProperty(key)) setRow(rows[key], false, '');
    }
  }

  function resizeSurface(fontSize) {
    var visibleRows = root ? root.querySelectorAll('.row.visible').length : 0;
    var logicalWidth = 220;
    var lineHeight = Math.max(18, Math.ceil(fontSize * 1.15));
    var logicalHeight = Math.max(24, visibleRows * lineHeight + 4);
    var scale = gameUiScale();
    var width = Math.ceil(logicalWidth * scale);
    var height = Math.ceil(logicalHeight * scale);
    var key = width + 'x' + height + '@' + scale.toFixed(4);

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

  function render(data) {
    if (!root) return;

    if (!data || data.visible !== true) {
      hideRows();
      root.classList.add('hidden');
      resizeSurface(16);
      return;
    }

    var fontSize = Math.max(10, num(data.fontSize, 16));
    root.classList.remove('hidden');
    root.style.fontSize = fontSize + 'px';
    root.style.color = data.color || '#ffffff';

    setRow(rows.armor, data.armorEnabled === true, data.armorText);
    setRow(rows.chance, data.chanceEnabled === true, data.chanceText);
    setRow(rows.angle, data.angleEnabled === true, data.angleText);
    setRow(rows.effpen, data.effPenEnabled === true, data.effPenText);
    setRow(rows.kill, data.killEnabled === true, data.killText);
    setRow(rows.gun, data.gunEnabled === true, data.gunText);

    resizeSurface(fontSize);
  }

  function readPayload() {
    var raw = '';
    try {
      raw = window.model && window.model.payload ? String(window.model.payload) : '';
    } catch (e) {
      raw = '';
    }

    if (raw === lastPayload) return false;
    lastPayload = raw;

    var data = {};
    try {
      data = JSON.parse(raw || '{}');
    } catch (e) {
      data = {};
    }

    render(data);
    return true;
  }

  function tick() {
    readPayload();
  }

  function refreshGeometry() {
    lastSize = null;
    tick();
  }

  function initialize() {
    resizeSurface(16);
    callModelCommand('onReady', {});
    tick();

    window.setTimeout(tick, 100);
    window.setTimeout(tick, 500);

    if (window.viewEnv && typeof viewEnv.addDataChangedCallback === 'function') {
      try { viewEnv.addDataChangedCallback('model', 0, true); } catch (e) {}
    }

    if (window.engine) {
      try { window.engine.on('viewEnv.onDataChanged', tick); } catch (e) {}
      try { window.engine.on('self.onScaleUpdated', refreshGeometry); } catch (e) {}
      try { window.engine.on('clientResized', refreshGeometry); } catch (e) {}
    }

    if (!pollTimer) pollTimer = window.setInterval(tick, 1000);
  }

  if (window.engine && window.engine.whenReady) {
    var domReady = window.isDomBuilt ? Promise.resolve() : new Promise(function (resolve) {
      try { window.engine.on('self.onDomBuilt', resolve); }
      catch (e) { resolve(); }
    });

    Promise.all([window.engine.whenReady, domReady]).then(function () {
      requestAnimationFrame(function () {
        requestAnimationFrame(initialize);
      });
    });
  } else {
    initialize();
  }
}());
