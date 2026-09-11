(function () {
  'use strict';

  var WIDTH = 220;
  var MIN_HEIGHT = 24;
  var NS = 'http://www.w3.org/2000/svg';
  var root = document.getElementById('armor-root');
  var holder = document.getElementById('armor-holder');
  var svg = document.getElementById('armor-hud');
  var lastPayload = null;
  var lastData = null;
  var lastSize = null;
  var logicalHeight = MIN_HEIGHT;
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

  function applyLogicalSize(height) {
    logicalHeight = Math.max(MIN_HEIGHT, Math.ceil(height || MIN_HEIGHT));
    try {
      document.documentElement.style.width = WIDTH + 'px';
      document.documentElement.style.height = logicalHeight + 'px';
      document.body.style.width = WIDTH + 'px';
      document.body.style.height = logicalHeight + 'px';
    } catch (e) {}
    if (root) {
      root.style.width = WIDTH + 'px';
      root.style.height = logicalHeight + 'px';
    }
    if (holder) {
      holder.style.width = WIDTH + 'px';
      holder.style.height = logicalHeight + 'px';
    }
    if (svg) {
      svg.setAttribute('width', WIDTH);
      svg.setAttribute('height', logicalHeight);
      svg.setAttribute('viewBox', '0 0 ' + WIDTH + ' ' + logicalHeight);
      svg.style.width = WIDTH + 'px';
      svg.style.height = logicalHeight + 'px';
    }
  }

  function resizeWindow(height) {
    applyLogicalSize(height);
    var scale = gameUiScale();
    var width = Math.ceil(WIDTH * scale);
    var physicalHeight = Math.ceil(logicalHeight * scale);
    var key = width + 'x' + physicalHeight + '@' + scale.toFixed(4);
    if (key === lastSize) return;
    lastSize = key;
    try {
      if (window.viewEnv && typeof viewEnv.resizeViewPx === 'function') {
        viewEnv.resizeViewPx(width, physicalHeight);
      }
    } catch (e) {}
    callModelCommand('onResized', { width: width, height: physicalHeight, gameScale: scale });
  }

  function clearSvg() {
    if (!svg) return;
    while (svg.firstChild) svg.removeChild(svg.firstChild);
  }

  function enabledRows(data) {
    var rows = [];
    if (!data) return rows;
    if (data.armorEnabled === true) rows.push(String(data.armorText || ''));
    if (data.chanceEnabled === true) rows.push(String(data.chanceText || ''));
    if (data.angleEnabled === true) rows.push(String(data.angleText || ''));
    if (data.effPenEnabled === true) rows.push(String(data.effPenText || ''));
    if (data.killEnabled === true) rows.push(String(data.killText || ''));
    if (data.gunEnabled === true) rows.push(String(data.gunText || ''));
    return rows;
  }

  function appendText(value, y, fontSize, color) {
    var text = document.createElementNS(NS, 'text');
    text.setAttribute('x', WIDTH / 2);
    text.setAttribute('y', y);
    text.setAttribute('fill', color || '#ffffff');
    text.setAttribute('font-size', fontSize);
    text.setAttribute('font-family', 'Arial, sans-serif');
    text.setAttribute('font-weight', '700');
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('stroke', '#000000');
    text.setAttribute('stroke-width', '2');
    text.setAttribute('paint-order', 'stroke');
    text.textContent = value;
    svg.appendChild(text);
  }

  function draw(data) {
    if (!root || !svg) return;
    clearSvg();

    var rows = enabledRows(data);
    if (!data || data.visible !== true || rows.length === 0) {
      root.className = 'hidden';
      resizeWindow(MIN_HEIGHT);
      return;
    }

    var fontSize = Math.max(10, num(data.fontSize, 16));
    var rowHeight = Math.ceil(fontSize + 4);
    var height = Math.max(MIN_HEIGHT, 4 + rows.length * rowHeight);
    resizeWindow(height);
    root.className = '';

    var baseline = 2 + fontSize * 0.82;
    var color = data.color || '#ffffff';
    for (var i = 0; i < rows.length; i++) {
      appendText(rows[i], baseline + i * rowHeight, fontSize, color);
    }
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
    lastData = data;
    draw(data);
    return true;
  }

  function tick() {
    readPayload();
  }

  function refreshGeometry() {
    lastSize = null;
    if (lastData) draw(lastData);
    else resizeWindow(MIN_HEIGHT);
  }

  function initialize() {
    resizeWindow(MIN_HEIGHT);
    tick();
    callModelCommand('onReady', {});

    window.setTimeout(tick, 100);
    window.setTimeout(tick, 500);

    if (window.viewEnv && viewEnv.addDataChangedCallback) {
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
