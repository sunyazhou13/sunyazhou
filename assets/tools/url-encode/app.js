/**
 * URL 编码解码 — 纯前端，内容不上传
 *
 * 文本与 %20 / %2F 等百分号编码双向互转，三种一键动作：
 *   - 编码：encodeURIComponent / encodeURI 两种模式可选
 *   - 解码：decodeURIComponent / decodeURI（非法 % 序列会定位报错）
 *   - 切换：⇄ 单次切换方向，便于在已编码 / 已解码文本间往返
 *
 * 类名前缀 ue-，与既有工具同构。
 * 页面结构见 /tools/url-encode.md
 */
(function () {
  'use strict';

  var ROOT = document.getElementById('ue-app');
  if (!ROOT) return;

  function $id(k) { return document.getElementById('ue-' + k); }
  var els = {
    comp: $id('comp'), uri: $id('uri'),
    src: $id('src'), dst: $id('dst'), status: $id('status'),
    srcTag: $id('src-tag'), dstTag: $id('dst-tag'),
    encode: $id('encode'), decode: $id('decode'),
    swap: $id('swap'), copy: $id('copy'), clear: $id('clear')
  };

  var state = { dir: 'encode' };

  function currentMode() { return els.comp.checked ? 'comp' : 'uri'; }
  function encodeFn(mode) { return mode === 'comp' ? encodeURIComponent : encodeURI; }
  function decodeFn(mode) { return mode === 'comp' ? decodeURIComponent : decodeURI; }

  function note(msg, warn) {
    els.status.textContent = msg || '';
    els.status.classList.toggle('ue-warn', !!warn);
  }

  function doEncode() {
    var mode = currentMode();
    var text = els.src.value;
    if (!text) { note('请输入要编码的内容'); return; }
    try {
      els.dst.value = encodeFn(mode)(text);
      state.dir = 'encode';
      els.srcTag.textContent = '输入（原文）';
      els.dstTag.textContent = '结果（% 编码）';
      note('已编码 · ' + els.dst.value.length + ' 个字符');
    } catch (e) {
      note('编码失败：' + (e && e.message || e));
    }
  }

  function doDecode() {
    var mode = currentMode();
    var text = els.src.value;
    if (!text) { note('请输入要解码的内容'); return; }
    try {
      els.dst.value = decodeFn(mode)(text);
      state.dir = 'decode';
      els.srcTag.textContent = '输入（% 编码）';
      els.dstTag.textContent = '结果（原文）';
      note('已解码 · ' + els.dst.value.length + ' 个字符');
    } catch (e) {
      note('解码失败：存在非法的百分号序列（% 后必须紧跟两位十六进制）');
    }
  }

  function doSwap() {
    var text = els.dst.value;
    if (!text) { note('结果区为空，没有可切换的内容'); return; }
    els.src.value = text;
    els.dst.value = '';
    if (state.dir === 'decode') doEncode(); else doDecode();
  }

  function copyResult() {
    var text = els.dst.value;
    if (!text) { note('结果区为空，无可复制内容'); return; }
    function done(ok) { note(ok ? '已复制到剪贴板' : '复制失败，请手动复制'); }
    if (navigator && navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function () { done(true); }, function () { done(false); });
    } else {
      var ta = document.createElement('textarea');
      ta.value = text; ta.style.position = 'fixed'; ta.style.opacity = '0';
      document.body.appendChild(ta); ta.select();
      var okk = false;
      try { okk = document.execCommand('copy'); } catch (e) { okk = false; }
      document.body.removeChild(ta);
      done(okk);
    }
  }

  function doClear() {
    els.src.value = '';
    els.dst.value = '';
    els.srcTag.textContent = '输入';
    els.dstTag.textContent = '结果';
    note('');
  }

  /* ---------- 事件绑定 ---------- */
  els.encode.addEventListener('click', doEncode);
  els.decode.addEventListener('click', doDecode);
  els.swap.addEventListener('click', doSwap);
  els.copy.addEventListener('click', copyResult);
  els.clear.addEventListener('click', doClear);

  els.comp.addEventListener('change', function () { note('当前模式：encodeURIComponent（参数值友好）'); });
  els.uri.addEventListener('change', function () { note('当前模式：encodeURI（URL 结构保留 / : ? # 等）'); });

  /* 输入即自动编码（防抖 250ms），方向默认编码 */
  var timer = null;
  els.src.addEventListener('input', function () {
    if (timer) clearTimeout(timer);
    timer = setTimeout(function () {
      if (els.src.value) doEncode();
    }, 250);
  });
})();
