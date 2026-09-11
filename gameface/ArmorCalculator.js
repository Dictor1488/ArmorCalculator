(function () {
  'use strict';

  var NS = 'http://www.w3.org/2000/svg';
  var WIDTH = 220;
  var MIN_HEIGHT = 24;
  var svg = document.getElementById('armor-svg');
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

  function clearSvg() {
    if (!svg) return;
    while (svg.firstChild) svg.removeChild(svg.firstChild);
  }

  function el(name, attrs, parent) {
    var node = document.createElementNS(NS, name);
    if (attrs) {
      for (var key in attrs) {
        if (attrs.hasOwnProperty(key)) node.setAttribute(key, attrs[key]);
      }
    }
    (parent || svg).appendChild(node);
    return node;
  }

  function addDefs() {
    var defs = el('defs');
    var filter = el('filter', { id: 'armorShadow', x: '-40%', y: '-80%', width: '180%', height: '260%' }, defs);
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
    var scale = gameUiScale();
    var width = Math.ceil(WIDTH * scale);
    var height = Math.ceil(logicalHeight * scale);
    var key = width + 'x' + height + '@' + scale.toFixed(4);

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
    var t = el('text', {
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

  function render(data) {
    if (!svg) return;
    clearSvg();

    if (!data || data.visible !== true) {
      resizeSurface(MIN_HEIGHT);
      return;
    }

    addDefs();

    var fontSize = Math.max(10, num(data.fontSize, 16));
    var lineHeight = Math.max(18, Math.ceil(fontSize * 1.2));
    var lines = [];

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

    var logicalHeight = Math.max(MIN_HEIGHT, lines.length * lineHeight + 4);
    resizeSurface(logicalHeight);

    var baselineOffset = fontSize * 0.82;
    for (var i = 0; i < lines.length; i++) {
      var top = 2 + i * lineHeight;
      drawText(lines[i], top + baselineOffset, fontSize, data.color || '#ffffff');
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
    resizeSurface(MIN_HEIGHT);
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

    if (!pollTimer) pollTimer = window.setInterval(tick, 250);
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
