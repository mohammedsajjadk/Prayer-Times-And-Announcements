/**
 * Debug Logging Module — LOCAL MODE ONLY
 *
 * Intercepts console.log and buffers entries, flushing every 3 seconds
 * to the server via POST /api/debug-log (which writes to logs/debug.log).
 *
 * This module does NOTHING in production — the IS_LOCAL guard ensures
 * no network requests are ever made from a live deployment.
 */
(function () {
  var IS_LOCAL = ['localhost', '127.0.0.1'].includes(window.location.hostname);
  if (!IS_LOCAL) return;

  var _buffer = [];
  var _flushing = false;

  // Detect the log endpoint prefix based on path (tralee = /, dublin = /dublin/)
  function _apiBase() {
    return window.location.pathname.startsWith('/dublin') ? '/dublin/' : '/';
  }

  var _originalLog = console.log.bind(console);
  var _originalWarn = console.warn.bind(console);
  var _originalError = console.error.bind(console);

  function _capture(level, args) {
    var ts = new Date().toISOString().replace('T', ' ').substring(0, 23);
    var msg = Array.prototype.slice.call(args).map(function (a) {
      if (a === null) return 'null';
      if (a === undefined) return 'undefined';
      if (typeof a === 'object') {
        try { return JSON.stringify(a); } catch (_) { return String(a); }
      }
      return String(a);
    }).join(' ');
    _buffer.push('[' + ts + '] [' + level + '] ' + msg);
  }

  console.log = function () {
    _originalLog.apply(console, arguments);
    _capture('LOG', arguments);
  };
  console.warn = function () {
    _originalWarn.apply(console, arguments);
    _capture('WARN', arguments);
  };
  console.error = function () {
    _originalError.apply(console, arguments);
    _capture('ERROR', arguments);
  };

  function _flush() {
    if (_flushing || _buffer.length === 0) return;
    _flushing = true;
    var lines = _buffer.slice();
    _buffer = [];
    fetch(_apiBase() + 'api/debug-log', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lines: lines }),
    }).catch(function () {
      // Server not reachable — silently discard; don't re-buffer to avoid memory growth
    }).finally(function () {
      _flushing = false;
    });
  }

  setInterval(_flush, 3000);

  // Flush on page unload (best-effort)
  window.addEventListener('beforeunload', _flush);
})();
