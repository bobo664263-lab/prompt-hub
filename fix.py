# encoding: utf-8
import re

with open(r'C:\Users\Lenovo\.openclaw-autoclaw\workspace\projects\prompt-hub\index.html', encoding='utf8') as f:
    html = f.read()

# 1. Add --gold variable
html = html.replace('--cyan: #00cec9;\n  --cyan-light: #e6fafa;', 
                    '--cyan: #00cec9;\n  --cyan-light: #e6fafa;\n  --gold: #f59e0b;\n  --gold-light: #fffbeb;')

# 2. Add badge-free/paid CSS
html = html.replace('.badge-model { background:var(--purple-light); color:var(--purple); }',
'.badge-model { background:var(--purple-light); color:var(--purple); }\n.badge-free { background:var(--green-light); color:var(--green); }\n.badge-paid { background:var(--gold-light); color:#b45309; }')

# 3. Add btn-unlock CSS
html = html.replace('.btn-detail:hover { background:var(--purple-light); color:var(--purple); }',
'.btn-detail:hover { background:var(--purple-light); color:var(--purple); }\n.btn-unlock { background:var(--gold); color:#fff; }\n.btn-unlock:hover { background:#d97706; }')

# 4. Add paid card blur CSS
old_blur = '.p-card .pc-preview::after { content:'
new_blur = '.p-card.paid .pc-preview-inner{filter:blur(3px);user-select:none}\n.p-card.paid .pc-lock{position:absolute;top:0;left:0;right:0;bottom:0;display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,0.5);border-radius:8px;cursor:pointer}\n.p-card .pc-preview::after { content:'
html = html.replace(old_blur, new_blur)

# 5. Add payment modal HTML
pay_html = '''\n<div class="modal-overlay" id="payModal" onclick="if(event.target===this)closePayModal()">
  <div class="modal" style="text-align:center;max-width:400px">
    <div style="font-size:2em;margin-bottom:8px">🔓</div>
    <h3>解锁全部付费提示词</h3>
    <p style="font-size:1.2em;font-weight:800;color:var(--gold);margin:8px 0">¥9.9<small style="font-size:0.5em;color:var(--text3);font-weight:400">/永久</small></p>
    <div style="display:flex;gap:12px;justify-content:center;margin:12px 0">
      <div><img src="qrcode-wx.jpg" style="width:120px;height:120px;border-radius:10px;border:1.5px solid var(--border);object-fit:cover"><div style="font-size:0.75em;font-weight:600;color:#07c160;margin-top:4px">微信</div></div>
      <div><img src="qrcode-zfb.jpg" style="width:120px;height:120px;border-radius:10px;border:1.5px solid var(--border);object-fit:cover"><div style="font-size:0.75em;font-weight:600;color:#1677ff;margin-top:4px">支付宝</div></div>
    </div>
    <button class="btn btn-primary" onclick="confirmPay()" id="payConfirmBtn" style="width:100%;justify-content:center">✅ 我已完成付款，立即解锁</button>
    <div style="text-align:left;font-size:0.78em;color:var(--text2);margin-top:10px">✓ 全部进阶+高级提示词解锁 · ✓ 后续新增自动解锁</div>
  </div>
</div>\n'''
html = html.replace('\n</footer>', pay_html + '</footer>')

# 6. Add tiering JS
tier_js = '\n\n// Free/paid tiering\nprompts.forEach(p => { p.free = (p.diff === "easy"); });\nconst unlocked = new Set(JSON.parse(localStorage.getItem("ph_unlocked")||"[]"));\n'
html = html.replace('\nconst featuredIds = prompts.filter', tier_js + 'const featuredIds = prompts.filter')

# 7. Modify renderAll - add isFree and change card template
old_map = 'document.getElementById("promptGrid").innerHTML = list.map(p => `'
new_map = 'document.getElementById("promptGrid").innerHTML = list.map(p => { const isFree = p.free || unlocked.has(p.title); return `'
html = html.replace(old_map, new_map)

old_join = '`).join(\'\')'
new_join = '`}).join(\'\')'
html = html.replace(old_join, new_join)

# 8. Modify card template - add classes, badges, unlock button
# Need to find and replace the entire card template
old_card_start = '    <div class="p-card">\n      <div class="pc-top">\n        <div class="pc-title">'
new_card_start = '    <div class="p-card${isFree?"":" paid"}">\n      <div class="pc-top">\n        <div class="pc-title">'
html = html.replace(old_card_start, new_card_start)

# Add free/paid badge in the badges section
old_badges = '<span class="badge badge-model">${p.model.split'
new_badges = '<span class="badge ${isFree?"badge-free":"badge-paid"}">${isFree?"免费":"付费"}</span>\n          <span class="badge badge-model">${p.model.split'
html = html.replace(old_badges, new_badges)

# Change preview div to include blur inner div and lock overlay
old_preview = '<div class="pc-preview">${escapeHtml(p.prompt.substring(0,120))}...</div>'
new_preview = '<div class="pc-preview">\n        <div class="pc-preview-inner">${escapeHtml(p.prompt.substring(0,120))}...</div>\n        ${isFree?"":"<div class=\\"pc-lock\\" onclick=\\"event.stopPropagation();openPayModal()\\">🔒</div>"}\n      </div>'
html = html.replace(old_preview, new_preview)

# Change bottom actions - conditional detail/copy vs unlock
old_btn1 = '<button class="btn-sm btn-detail"'
old_btn2 = '<button class="btn-sm btn-copy"'

# Find the exact line with both buttons
old_actions = '<button class="btn-sm btn-detail" onclick="openModal(' + "'" + '${p.title.replace(/' + "'" + '/g,"' + "\\\\" + "'" + '")}' + "'" + ')">详情</button>\n          <button class="btn-sm btn-copy" onclick="copyPrompt(' + "'" + '${p.title.replace(/' + "'" + '/g,"' + "\\\\" + "'" + '")}' + "'" + ',this)">复制</button>'

new_actions = '${isFree?"<button class=\\"btn-sm btn-detail\\" onclick=\\"openModal(' + "'" + '${p.title.replace(/' + "'" + '/g,"' + "\\\\\\\\" + "'" + '")}' + "'" + ')\\">详情</button><button class=\\"btn-sm btn-copy\\" onclick=\\"copyPrompt(' + "'" + '${p.title.replace(/' + "'" + '/g,"' + "\\\\\\\\" + "'" + '")}' + "'" + ',this)\\">复制</button>":"<button class=\\"btn-sm btn-unlock\\" onclick=\\"event.stopPropagation();openPayModal()\\">🔓 解锁 ¥9.9</button>"}'

html = html.replace(old_actions, new_actions)

# 9. Add payment JS functions
pay_js = '''
function openPayModal(){ document.getElementById("payModal").classList.add("show"); }
function closePayModal(){ document.getElementById("payModal").classList.remove("show"); }
function confirmPay(){
  prompts.filter(p=>!p.free).forEach(p=>unlocked.add(p.title));
  localStorage.setItem("ph_unlocked",JSON.stringify([...unlocked]));
  var b=document.getElementById("payConfirmBtn");
  b.textContent="✅ 解锁成功！"; b.style.background="var(--green)";
  setTimeout(function(){ closePayModal(); renderAll(); },1000);
}
'''
html = html.replace('\n\nrenderCatGrid();', pay_js + '\nrenderCatGrid();')

# 10. Update escape key handler
html = html.replace("document.addEventListener('keydown', e => { if (e.key === 'Escape') closeModal(); });",
"document.addEventListener('keydown', e => { if (e.key === 'Escape') { closeModal(); closePayModal(); } });")

with open(r'C:\Users\Lenovo\.openclaw-autoclaw\workspace\projects\prompt-hub\index.html', 'w', encoding='utf8') as f:
    f.write(html)
print('DONE')
