/**
 * 时间戳转换工具 — 纯前端实现，无外部依赖
 *
 * 功能：
 *   - 实时显示当前日期时间（精确到毫秒，每 50ms 刷新）
 *   - 时间戳 → 日期（自动识别秒/毫秒/Apple Double 带小数）
 *   - 日期 → 时间戳（输出秒/毫秒/Apple Double 三种格式）
 *   - Swift / Objective-C 获取时间戳的 API 示例
 *
 * Apple 时间戳说明：
 *   NSDate.timeIntervalSince1970 返回 Double，整数部分为秒，
 *   小数部分为毫秒（如 1692800123.456）。
 *
 * 资源全部位于 /assets/tools/timestamp/，与博客其它功能零耦合。
 * 页面结构见 /tools/timestamp.md
 */

(function () {
  'use strict';

  var root = document.getElementById('ts-app');
  if (!root) return;

  var els = {
    nowDate: document.getElementById('ts-now-date'),
    nowTime: document.getElementById('ts-now-time'),
    nowMs: document.getElementById('ts-now-ms'),
    nowTs: document.getElementById('ts-now-ts'),
    nowTsMs: document.getElementById('ts-now-ts-ms'),
    nowTsApple: document.getElementById('ts-now-ts-apple'),
    nowIso: document.getElementById('ts-now-iso'),
    copyNow: document.getElementById('ts-copy-now'),

    tsInput: document.getElementById('ts-input'),
    tsConvert: document.getElementById('ts-convert'),
    tsResult: document.getElementById('ts-result'),

    dateInput: document.getElementById('ts-date-input'),
    timeInput: document.getElementById('ts-time-input'),
    msInput: document.getElementById('ts-ms-input'),
    dateConvert: document.getElementById('ts-date-convert'),
    dateResult: document.getElementById('ts-date-result'),

    codeTabs: document.getElementById('ts-code-tabs'),
    codeOutput: document.getElementById('ts-code-output'),
    copyCode: document.getElementById('ts-copy-code'),

    error: document.getElementById('ts-error')
  };

  var state = {
    activeLang: 'swift',
    clockTimer: null
  };

  function txt(n) { return n == null ? '' : String(n); }

  function pad(n, len) {
    len = len || 2;
    var s = '000' + n;
    return s.slice(s.length - len);
  }

  function showError(msg) {
    if (!els.error) return;
    els.error.textContent = msg;
    els.error.hidden = false;
  }

  function clearError() {
    if (!els.error) return;
    els.error.textContent = '';
    els.error.hidden = true;
  }

  /* ---------- 实时时钟 ---------- */

  function updateClock() {
    var now = new Date();
    var Y = now.getFullYear();
    var Mo = pad(now.getMonth() + 1);
    var D = pad(now.getDate());
    var H = pad(now.getHours());
    var Mi = pad(now.getMinutes());
    var S = pad(now.getSeconds());
    var Ms = pad(now.getMilliseconds(), 3);
    var weekday = now.getDay();
    var WEEKDAYS = ['日', '一', '二', '三', '四', '五', '六'];

    if (els.nowDate) els.nowDate.textContent = Y + '-' + Mo + '-' + D + ' 星期' + WEEKDAYS[weekday];
    if (els.nowTime) els.nowTime.textContent = H + ':' + Mi + ':' + S;
    if (els.nowMs) els.nowMs.textContent = '.' + Ms;

    var tsSec = Math.floor(now.getTime() / 1000);
    var tsMs = now.getTime();
    var tsApple = (now.getTime() / 1000).toFixed(3);
    var iso = now.toISOString();

    if (els.nowTs) els.nowTs.textContent = txt(tsSec);
    if (els.nowTsMs) els.nowTsMs.textContent = txt(tsMs);
    if (els.nowTsApple) els.nowTsApple.textContent = tsApple;
    if (els.nowIso) els.nowIso.textContent = iso;
  }

  function startClock() {
    updateClock();
    if (state.clockTimer) clearInterval(state.clockTimer);
    state.clockTimer = setInterval(updateClock, 50);
  }

  /* ---------- 时间戳 → 日期 ---------- */

  /* 自动识别时间戳格式：
     - 10 位整数 → 秒
     - 13 位整数 → 毫秒
     - 带小数点 → Apple Double（秒.毫秒） */
  function parseTimestamp(input) {
    var s = input.trim();
    if (!s) return null;

    var hasDot = s.indexOf('.') !== -1;
    var num = parseFloat(s);
    if (isNaN(num)) return null;

    /* Apple Double: 秒.毫秒（如 1692800123.456） */
    if (hasDot) {
      return new Date(num * 1000);
    }

    /* 整数：13 位 → 毫秒，10 位 → 秒，其他按长度猜 */
    if (s.length >= 13) {
      return new Date(num); /* 毫秒 */
    } else {
      return new Date(num * 1000); /* 秒 */
    }
  }

  function formatDate(d) {
    var Y = d.getFullYear();
    var Mo = pad(d.getMonth() + 1);
    var D = pad(d.getDate());
    var H = pad(d.getHours());
    var Mi = pad(d.getMinutes());
    var S = pad(d.getSeconds());
    var Ms = pad(d.getMilliseconds(), 3);
    var weekday = d.getDay();
    var WEEKDAYS = ['日', '一', '二', '三', '四', '五', '六'];

    var local = Y + '-' + Mo + '-' + D + ' ' + H + ':' + Mi + ':' + S + '.' + Ms + ' 星期' + WEEKDAYS[weekday];
    var utc = d.toISOString();
    var tsSec = Math.floor(d.getTime() / 1000);
    var tsMs = d.getTime();
    var tsApple = (d.getTime() / 1000).toFixed(3);

    return {
      local: local,
      utc: utc,
      iso: d.toISOString(),
      tsSec: tsSec,
      tsMs: tsMs,
      tsApple: tsApple,
      tsInput: txt(tsSec)
    };
  }

  function doConvertTs() {
    clearError();
    var input = els.tsInput.value;
    if (!input.trim()) {
      showError('请输入时间戳');
      els.tsResult.innerHTML = '';
      return;
    }

    var d = parseTimestamp(input);
    if (!d || isNaN(d.getTime())) {
      showError('无法解析时间戳，请检查输入');
      els.tsResult.innerHTML = '';
      return;
    }

    var fmt = formatDate(d);
    var html = '';
    html += '<div class="ts-res-item"><span class="ts-res-label">本地时间</span><code class="ts-res-val">' + fmt.local + '</code></div>';
    html += '<div class="ts-res-item"><span class="ts-res-label">UTC 时间</span><code class="ts-res-val">' + fmt.utc + '</code></div>';
    html += '<div class="ts-res-item"><span class="ts-res-label">ISO 8601</span><code class="ts-res-val">' + fmt.iso + '</code></div>';
    html += '<div class="ts-res-item"><span class="ts-res-label">Unix 秒</span><code class="ts-res-val">' + fmt.tsSec + '</code><button type="button" class="ts-btn ts-btn-copy" data-copy-value="' + fmt.tsSec + '">复制</button></div>';
    html += '<div class="ts-res-item"><span class="ts-res-label">Unix 毫秒</span><code class="ts-res-val">' + fmt.tsMs + '</code><button type="button" class="ts-btn ts-btn-copy" data-copy-value="' + fmt.tsMs + '">复制</button></div>';
    html += '<div class="ts-res-item"><span class="ts-res-label">Apple Double</span><code class="ts-res-val">' + fmt.tsApple + '</code><button type="button" class="ts-btn ts-btn-copy" data-copy-value="' + fmt.tsApple + '">复制</button></div>';

    els.tsResult.innerHTML = html;
  }

  /* ---------- 日期 → 时间戳 ---------- */

  function doConvertDate() {
    clearError();
    var dateStr = els.dateInput.value;
    var timeStr = els.timeInput.value || '00:00:00';
    var msStr = els.msInput.value || '0';

    if (!dateStr) {
      showError('请选择日期');
      els.dateResult.innerHTML = '';
      return;
    }

    var parts = dateStr.split('-');
    if (parts.length !== 3) {
      showError('日期格式错误');
      els.dateResult.innerHTML = '';
      return;
    }

    var Y = parseInt(parts[0], 10);
    var Mo = parseInt(parts[1], 10) - 1;
    var D = parseInt(parts[2], 10);

    var timeParts = timeStr.split(':');
    var H = parseInt(timeParts[0], 10) || 0;
    var Mi = parseInt(timeParts[1], 10) || 0;
    var S = parseInt(timeParts[2], 10) || 0;
    var Ms = parseInt(msStr, 10) || 0;

    if (Ms < 0 || Ms > 999) {
      showError('毫秒应在 0-999 范围内');
      els.dateResult.innerHTML = '';
      return;
    }

    var d = new Date(Y, Mo, D, H, Mi, S, Ms);
    if (isNaN(d.getTime())) {
      showError('日期无效，请检查输入');
      els.dateResult.innerHTML = '';
      return;
    }

    var tsSec = Math.floor(d.getTime() / 1000);
    var tsMs = d.getTime();
    var tsApple = (d.getTime() / 1000).toFixed(3);
    var iso = d.toISOString();

    var html = '';
    html += '<div class="ts-res-item"><span class="ts-res-label">Unix 秒</span><code class="ts-res-val">' + tsSec + '</code><button type="button" class="ts-btn ts-btn-copy" data-copy-value="' + tsSec + '">复制</button></div>';
    html += '<div class="ts-res-item"><span class="ts-res-label">Unix 毫秒</span><code class="ts-res-val">' + tsMs + '</code><button type="button" class="ts-btn ts-btn-copy" data-copy-value="' + tsMs + '">复制</button></div>';
    html += '<div class="ts-res-item"><span class="ts-res-label">Apple Double</span><code class="ts-res-val">' + tsApple + '</code><button type="button" class="ts-btn ts-btn-copy" data-copy-value="' + tsApple + '">复制</button></div>';
    html += '<div class="ts-res-item"><span class="ts-res-label">ISO 8601</span><code class="ts-res-val">' + iso + '</code></div>';
    html += '<div class="ts-res-item"><span class="ts-res-label">本地确认</span><code class="ts-res-val">' + formatDate(d).local + '</code></div>';

    els.dateResult.innerHTML = html;
  }

  /* ---------- 代码片段 ---------- */

  function generateCode() {
    var lang = state.activeLang;
    var code = '';
    if (lang === 'swift') code = genSwiftCode();
    else code = genObjCCode();
    els.codeOutput.innerHTML = highlightCode(code);
  }

  function genSwiftCode() {
    var L = [];
    L.push('// MARK: - 获取当前时间戳');
    L.push('');
    L.push('// 秒级时间戳（Double，Apple 标准格式，带小数毫秒）');
    L.push('let tsApple = Date().timeIntervalSince1970');
    L.push('// 如: 1692800123.456');
    L.push('');
    L.push('// 秒级整数时间戳');
    L.push('let tsSec = Int(Date().timeIntervalSince1970)');
    L.push('');
    L.push('// 毫秒级整数时间戳');
    L.push('let tsMs = Int(Date().timeIntervalSince1970 * 1000)');
    L.push('');
    L.push('// 纯整数方式（CFAbsoluteTime）');
    L.push('let absTime = CFAbsoluteTimeGetCurrent() + 978307200');
    L.push('// CFAbsoluteTime 从 2001-01-01 起，需加 978307200 转为 1970 起');
    L.push('');
    L.push('// MARK: - 时间戳 → Date');
    L.push('');
    L.push('// Apple Double（秒.毫秒）→ Date');
    L.push('let date = Date(timeIntervalSince1970: 1692800123.456)');
    L.push('');
    L.push('// 毫秒整数 → Date');
    L.push('let date2 = Date(timeIntervalSince1970: TimeInterval(1692800123456) / 1000)');
    L.push('');
    L.push('// 秒整数 → Date');
    L.push('let date3 = Date(timeIntervalSince1970: TimeInterval(1692800123))');
    L.push('');
    L.push('// MARK: - Date → 格式化字符串');
    L.push('');
    L.push('let formatter = DateFormatter()');
    L.push('formatter.dateFormat = "yyyy-MM-dd HH:mm:ss.SSS"');
    L.push('formatter.timeZone = TimeZone.current');
    L.push('let str = formatter.string(from: date)');
    L.push('// 如: "2023-08-23 18:28:43.456"');
    L.push('');
    L.push('// MARK: - 获取当前时间各分量');
    L.push('');
    L.push('let cal = Calendar.current');
    L.push('let comp = cal.dateComponents([.year, .month, .day, .hour, .minute, .second, .nanosecond], from: Date())');
    L.push('let ms = comp.nanosecond! / 1_000_000  // 纳秒 → 毫秒');
    L.push('');
    L.push('// MARK: - ISO8601 格式');
    L.push('');
    L.push('let isoStr = ISO8601DateFormatter().string(from: date)');
    L.push('// 如: "2023-08-23T10:28:43Z"');
    L.push('');
    L.push('// 带毫秒的 ISO8601');
    L.push('let isoFmt = ISO8601DateFormatter()');
    L.push('isoFmt.formatOptions = [.withInternetDateTime, .withFractionalSeconds]');
    L.push('let isoMs = isoFmt.string(from: date)');
    L.push('// 如: "2023-08-23T10:28:43.456Z"');
    return L.join('\n');
  }

  function genObjCCode() {
    var L = [];
    L.push('#pragma mark - 获取当前时间戳');
    L.push('');
    L.push('// 秒级时间戳（Double，Apple 标准格式，带小数毫秒）');
    L.push('NSTimeInterval tsApple = [[NSDate date] timeIntervalSince1970];');
    L.push('// 如: 1692800123.456');
    L.push('');
    L.push('// 秒级整数时间戳');
    L.push('NSInteger tsSec = (NSInteger)[[NSDate date] timeIntervalSince1970];');
    L.push('');
    L.push('// 毫秒级整数时间戳');
    L.push('NSInteger tsMs = (NSInteger)([[NSDate date] timeIntervalSince1970] * 1000);');
    L.push('');
    L.push('#pragma mark - 时间戳 → NSDate');
    L.push('');
    L.push('// Apple Double（秒.毫秒）→ NSDate');
    L.push('NSDate *date = [NSDate dateWithTimeIntervalSince1970:1692800123.456];');
    L.push('');
    L.push('// 毫秒整数 → NSDate');
    L.push('NSDate *date2 = [NSDate dateWithTimeIntervalSince1970:(NSTimeInterval)1692800123456 / 1000];');
    L.push('');
    L.push('// 秒整数 → NSDate');
    L.push('NSDate *date3 = [NSDate dateWithTimeIntervalSince1970:(NSTimeInterval)1692800123];');
    L.push('');
    L.push('#pragma mark - NSDate → 格式化字符串');
    L.push('');
    L.push('NSDateFormatter *fmt = [NSDateFormatter new];');
    L.push('fmt.dateFormat = @"yyyy-MM-dd HH:mm:ss.SSS";');
    L.push('fmt.timeZone = [NSTimeZone localTimeZone];');
    L.push('NSString *str = [fmt stringFromDate:date];');
    L.push('// 如: @"2023-08-23 18:28:43.456"');
    L.push('');
    L.push('#pragma mark - 获取当前时间各分量');
    L.push('');
    L.push('NSCalendar *cal = [NSCalendar currentCalendar];');
    L.push('NSDateComponents *comp = [cal components:(NSCalendarUnitYear | NSCalendarUnitMonth |');
    L.push('    NSCalendarUnitDay | NSCalendarUnitHour | NSCalendarUnitMinute |');
    L.push('    NSCalendarUnitSecond | NSCalendarUnitNanosecond) fromDate:[NSDate date]];');
    L.push('NSInteger ms = comp.nanosecond / 1000000;  // 纳秒 → 毫秒');
    L.push('');
    L.push('#pragma mark - ISO8601 格式');
    L.push('');
    L.push('NSISO8601DateFormatter *isoFmt = [NSISO8601DateFormatter new];');
    L.push('isoFmt.formatOptions = NSISO8601DateFormatWithInternetDateTime |');
    L.push('                       NSISO8601DateFormatWithFractionalSeconds;');
    L.push('NSString *isoStr = [isoFmt stringFromDate:date];');
    L.push('// 如: @"2023-08-23T10:28:43.456Z"');
    L.push('');
    L.push('#pragma mark - 性能计时（高精度）');
    L.push('');
    L.push('// mach_absolute_time 适合微观级计时（纳秒精度）');
    L.push('uint64_t start = mach_absolute_time();');
    L.push('// ... 执行耗时操作 ...');
    L.push('uint64_t elapsed = mach_absolute_time() - start;');
    L.push('mach_timebase_info_data_t info;');
    L.push('mach_timebase_info(&info);');
    L.push('double seconds = (double)elapsed * info.numer / info.denom / 1e9;');
    return L.join('\n');
  }

  /* ---------- 轻量语法高亮 ---------- */

  function highlightCode(code) {
    var s = code.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    var re = /(\/\/[^\n]*)|(#pragma[^\n]*)|('[^']*'|"[^"]*")|(#[0-9A-Fa-f]{3,8}\b)|(0x[0-9A-Fa-f]+)|(\b\d+\.?\d*[fF]?\b)|\b(let|var|Int|Double|TimeInterval|Date|DateFormatter|ISO8601DateFormatter|Calendar|NSCalendar|NSDate|NSDateFormatter|NSISO8601DateFormatter|NSDateComponents|NSString|NSInteger|NSTimeInterval|NSUInteger|uint64_t|BOOL|CFAbsoluteTime|CGFloat|NSCalendarUnit)\b|(@[a-zA-Z]+)|(\.[a-zA-Z_][a-zA-Z0-9_]*)/g;
    return s.replace(re, function(m, c1, c2, s1, h, n1, n2, k, a, p) {
      if (c1 || c2) return '<span class="ts-tok-c">' + m + '</span>';
      if (s1) return '<span class="ts-tok-s">' + m + '</span>';
      if (h || n1 || n2) return '<span class="ts-tok-n">' + m + '</span>';
      if (k) return '<span class="ts-tok-k">' + m + '</span>';
      if (a) return '<span class="ts-tok-a">' + m + '</span>';
      if (p) return '<span class="ts-tok-p">' + m + '</span>';
      return m;
    });
  }

  /* ---------- 复制 ---------- */

  function copyFallback(text) {
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.style.position = 'fixed';
    ta.style.opacity = '0';
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand('copy'); } catch (e) {}
    ta.remove();
  }

  function flashCopied(btn) {
    var old = btn.textContent;
    btn.textContent = '已复制';
    btn.classList.add('ts-copied');
    clearTimeout(btn._t);
    btn._t = setTimeout(function () {
      btn.textContent = old;
      btn.classList.remove('ts-copied');
    }, 1200);
  }

  function copyText(text, btn) {
    function done() { flashCopied(btn); }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(done, function () {
        copyFallback(text);
        done();
      });
    } else {
      copyFallback(text);
      done();
    }
  }

  /* ---------- 事件 ---------- */

  els.tsConvert.addEventListener('click', doConvertTs);
  els.tsInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter') doConvertTs();
  });

  els.dateConvert.addEventListener('click', doConvertDate);

  /* Tab 切换 */
  els.codeTabs.addEventListener('click', function (e) {
    var btn = e.target;
    while (btn && btn !== els.codeTabs && !(btn.getAttribute && btn.getAttribute('data-lang'))) {
      btn = btn.parentNode;
    }
    if (!btn || btn === els.codeTabs) return;
    var lang = btn.getAttribute('data-lang');
    state.activeLang = lang;
    var tabs = els.codeTabs.querySelectorAll('.ts-tab');
    for (var i = 0; i < tabs.length; i++) {
      tabs[i].classList.toggle('ts-tab-active', tabs[i] === btn);
    }
    generateCode();
  });

  /* 复制：事件委托 */
  root.addEventListener('click', function (e) {
    /* 单值复制 */
    var btn = e.target;
    while (btn && btn !== root && !(btn.getAttribute && btn.getAttribute('data-copy-value'))) {
      btn = btn.parentNode;
    }
    if (btn !== root && btn.getAttribute && btn.getAttribute('data-copy-value')) {
      copyText(btn.getAttribute('data-copy-value'), btn);
      return;
    }
    /* 当前时间戳复制 */
    if (e.target === els.copyNow || (e.target.parentNode === els.copyNow)) {
      copyText(els.nowTsApple.textContent, els.copyNow);
    }
    /* 代码复制 */
    if (e.target === els.copyCode || (e.target.parentNode === els.copyCode)) {
      copyText(els.codeOutput.textContent, els.copyCode);
    }
  });

  /* ---------- 启动 ---------- */

  clearError();
  startClock();
  generateCode();

  /* 页面卸载时清理定时器 */
  window.addEventListener('beforeunload', function () {
    if (state.clockTimer) clearInterval(state.clockTimer);
  });
})();
