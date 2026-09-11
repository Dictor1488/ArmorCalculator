(function () {
  'use strict';

  var WIDTH = 220;
  var HEIGHT = 24;
  var NS = 'http://www.w3.org/2000/svg';
  var root = document.getElementById('armor-root');
  var holder = document.getElementById('armor-holder');
  var svg = document.getElementById('armor-hud');
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

  function resizeWindow() {
    var scale = gameUiScale();
    var width = Math.ceil(WIDTH * scale);
    var height = Math.ceil(HEIGHT * scale);
    var key = width + 'x' + height + '@' + scale.toFixed(4);
    if (key === lastSize) return;
    lastSize = key;
    try {
      if (window.viewEnv && typeof viewEnv.resizeViewPx === 'function') {
        viewEnv.resizeViewPx(width, height);
      }
    } catch (e) {}
    callModelCommand('onResized', { width: width, height: height, gameScale: scale });
  }

  function clearSvg() {
    if (!svg) return;
    while (svg.firstChild) svg.removeChild(svg.firstChild);
  }

  function draw(data) {
    if (!root || !svg) return;
    clearSvg();

    if (!data || data.visible !== true || data.armorEnabled !== true) {
      root.className = 'hidden';
      return;
    }

    root.className = '';
    var fontSize = Math.max(10, num(data.fontSize, 16));
    var text = document.createElementNS(NS, 'text');
    text.setAttribute('x', WIDTH / 2);
    text.setAttribute('y', 2 + fontSize * 0.82);
    text.setAttribute('fill', data.color || '#ffffff');
    text.setAttribute('font-size', fontSize);
    text.setAttribute('font-family', 'Arial, sans-serif');
    text.setAttribute('font-weight', '700');
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('stroke', '#000000');
    text.setAttribute('stroke-width', '2');
    text.setAttribute('paint-order', 'stroke');
    text.textContent = String(data.armorText || '');
    svg.appendChild(text);
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
    draw(data);
    return true;
  }

  function tick() {
    readPayload();
  }

  function refreshGeometry() {
    lastSize = null;
    resizeWindow();
    tick();
  }

  function initialize() {
    resizeWindow();
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
