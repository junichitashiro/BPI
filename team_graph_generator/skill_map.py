"""
スキルマップジェネレーター
--------------------------
Excelファイル（メンバー / スキル の2シート）を読み込み、
ヒートマップ・表形式で切り替えられるスキルマップHTMLを出力する。
"""

import pandas as pd
import sys
import json

# ── 設定 ────────────────────────────────────────────────
EXCEL_PATH  = "team.xlsx"
OUTPUT_HTML = "skill_map.html"

# チームカラー
TEAM_COLORS = {
    "A": "#5B8CF0",
    "B": "#E8773A",
    "C": "#7B61E8",
}

# ── Excelを読み込む ──────────────────────────────────────
def load_excel(path: str):
    members = pd.read_excel(path, sheet_name="メンバー")
    skills  = pd.read_excel(path, sheet_name="スキル")
    return members, skills

# ── データ整形 ────────────────────────────────────────────
def build_matrix(members, skills):
    all_skills  = sorted(skills["スキル"].unique().tolist())
    member_list = members["氏名"].tolist()

    # 保有フラグ行列
    matrix = {}
    for name in member_list:
        owned = set(skills[skills["氏名"] == name]["スキル"].tolist())
        matrix[name] = {s: 1 if s in owned else 0 for s in all_skills}

    # スキルごとの保有人数
    skill_counts = {s: sum(matrix[n][s] for n in member_list) for s in all_skills}

    # メンバー情報
    member_info = members.set_index("氏名")[["役割", "チーム"]].to_dict("index")

    return member_list, all_skills, matrix, skill_counts, member_info

# ── HTML生成 ──────────────────────────────────────────────
def generate_html(member_list, all_skills, matrix, skill_counts, member_info):

    # Pythonデータ → JS用JSON
    js_matrix       = json.dumps(matrix,       ensure_ascii=False)
    js_members      = json.dumps(member_list,  ensure_ascii=False)
    js_skills       = json.dumps(all_skills,   ensure_ascii=False)
    js_skill_counts = json.dumps(skill_counts, ensure_ascii=False)
    js_member_info  = json.dumps(member_info,  ensure_ascii=False)
    js_team_colors  = json.dumps(TEAM_COLORS,  ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>スキルマップ</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: "Hiragino Sans", "Meiryo", sans-serif;
    background: #f4f5f7;
    color: #2c2c2a;
    padding: 24px;
  }}
  .wrapper {{
    display: table;
  }}
  h1 {{
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 16px;
    color: #1a1a18;
  }}

  /* ── コントロールバー ── */
  .controls {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
    flex-wrap: wrap;
  }}
  .tab-group {{
    display: flex;
    border: 1px solid #ccc;
    border-radius: 6px;
    overflow: hidden;
  }}
  .tab-btn {{
    padding: 7px 18px;
    font-size: 13px;
    border: none;
    background: #fff;
    cursor: pointer;
    transition: background .15s;
  }}
  .tab-btn.active {{
    background: #5B8CF0;
    color: #fff;
    font-weight: 600;
  }}
  .filter-label {{
    font-size: 13px;
    color: #555;
  }}
  select {{
    padding: 6px 10px;
    font-size: 13px;
    border: 1px solid #ccc;
    border-radius: 6px;
    background: #fff;
    cursor: pointer;
  }}

  /* ── 共通テーブル ── */
  .table-wrap {{
    overflow-x: auto;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    background: #fff;
  }}
  table {{
    border-collapse: collapse;
    width: max-content;
    max-width: 100%;
    font-size: 13px;
  }}
  th, td {{
    padding: 9px 14px;
    white-space: nowrap;
  }}
  thead th {{
    background: #f0f2f8;
    font-weight: 600;
    border-bottom: 2px solid #dde1f0;
    position: sticky;
    top: 0;
    z-index: 2;
  }}

  /* ── ヒートマップ ── */
  .hm-member-col {{
    position: sticky;
    left: 0;
    background: #fff;
    z-index: 1;
    border-right: 1px solid #e0e0e0;
    font-weight: 600;
    width: 390px;
    min-width: 390px;
    max-width: 390px;
    overflow: hidden;
    text-overflow: ellipsis;
  }}
  .hm-skill-th {{
    writing-mode: vertical-lr;
    padding: 12px 6px;
    font-size: 12px;
    max-height: 120px;
  }}
  .hm-cell {{
    text-align: center;
    width: 36px;
  }}
  .hm-cell.has {{
    background: #5B8CF0;
    color: #fff;
    font-size: 11px;
    font-weight: 700;
  }}
  .hm-cell.none {{
    background: #f4f5f7;
    color: #ccc;
  }}
  .hm-count-row td {{
    background: #eef1fb;
    font-size: 11px;
    text-align: center;
    color: #555;
    font-weight: 600;
    border-top: 2px solid #dde1f0;
  }}
  .risk {{ color: #E8A030; font-weight: 700; }}

  /* ── 表形式 ── */
  .tbl-name {{ font-weight: 600; }}
  .tbl-team-badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 11px;
    color: #fff;
    font-weight: 600;
  }}
  .tbl-skills {{
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }}
  .skill-tag {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 11px;
    background: #e8f0fe;
    color: #3a5fcf;
    font-weight: 500;
  }}
  .tbl-count {{
    text-align: center;
    font-weight: 600;
    color: #555;
  }}
  tbody tr:nth-child(even) td {{ background: #fafbff; }}

  /* ── サマリーバー ── */
  .summary {{
    display: flex;
    gap: 16px;
    margin-bottom: 16px;
    flex-wrap: wrap;
  }}
  .summary-card {{
    background: #fff;
    border-radius: 8px;
    padding: 12px 18px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    font-size: 12px;
    color: #666;
  }}
  .summary-card .val {{
    font-size: 22px;
    font-weight: 700;
    color: #1a1a18;
    display: block;
  }}
</style>
</head>
<body>

<div class="wrapper">

<h1>スキルマップ</h1>

<div class="summary" id="summary"></div>

<div class="controls">
  <div class="tab-group">
    <button class="tab-btn active" onclick="switchView('heatmap')">ヒートマップ</button>
    <button class="tab-btn"        onclick="switchView('table')">表形式</button>
  </div>
  <span class="filter-label">チーム:</span>
  <select id="team-filter" onchange="render()">
    <option value="">すべて</option>
  </select>
  <span class="filter-label">スキル:</span>
  <select id="skill-filter" onchange="render()">
    <option value="">すべて</option>
  </select>
</div>

<div class="table-wrap">
  <div id="view-area"></div>
</div>

</div><!-- /.wrapper -->

<script>
const MATRIX      = {js_matrix};
const MEMBERS     = {js_members};
const SKILLS      = {js_skills};
const SKILL_COUNTS= {js_skill_counts};
const MEMBER_INFO = {js_member_info};
const TEAM_COLORS = {js_team_colors};

let currentView = 'heatmap';

// ── 初期化 ────────────────────────────────────────────────
(function init() {{
  const teams = [...new Set(MEMBERS.map(m => MEMBER_INFO[m].チーム))].sort();
  const tSel  = document.getElementById('team-filter');
  teams.forEach(t => {{
    const o = document.createElement('option');
    o.value = t; o.textContent = 'チーム' + t;
    tSel.appendChild(o);
  }});

  const sSel = document.getElementById('skill-filter');
  SKILLS.forEach(s => {{
    const o = document.createElement('option');
    o.value = s; o.textContent = s;
    sSel.appendChild(o);
  }});

  renderSummary();
  render();
}})();

function renderSummary() {{
  const total     = MEMBERS.length;
  const skillNum  = SKILLS.length;
  const riskSkills= SKILLS.filter(s => SKILL_COUNTS[s] <= 2).length;
  const avgSkills = (MEMBERS.reduce((a, m) => a + SKILLS.filter(s => MATRIX[m][s]).length, 0) / total).toFixed(1);

  document.getElementById('summary').innerHTML = `
    <div class="summary-card"><span class="val">${{total}}</span>メンバー数</div>
    <div class="summary-card"><span class="val">${{skillNum}}</span>スキル種別数</div>
    <div class="summary-card"><span class="val">${{avgSkills}}</span>平均スキル数／人</div>
    <div class="summary-card"><span class="val" style="color:#E8A030">${{riskSkills}}</span>偏りリスクスキル（保有2人以下）</div>
  `;
}}

// ── フィルター適用 ─────────────────────────────────────────
function filteredData() {{
  const teamF  = document.getElementById('team-filter').value;
  const skillF = document.getElementById('skill-filter').value;

  const members = MEMBERS.filter(m =>
    !teamF || MEMBER_INFO[m].チーム === teamF
  );
  const skills = SKILLS.filter(s =>
    !skillF || s === skillF
  );
  return {{ members, skills }};
}}

// ── ビュー切替 ────────────────────────────────────────────
function switchView(view) {{
  currentView = view;
  document.querySelectorAll('.tab-btn').forEach((btn, i) => {{
    btn.classList.toggle('active', (i === 0) === (view === 'heatmap'));
  }});
  render();
  // ビュー切替後にwrapperの幅をコンテンツに合わせてリセット
  var w = document.querySelector('.wrapper');
  w.style.display = 'none';
  w.offsetHeight; // reflow
  w.style.display = 'table';
}}

function render() {{
  currentView === 'heatmap' ? renderHeatmap() : renderTable();
}}

// ── ヒートマップ ──────────────────────────────────────────
function renderHeatmap() {{
  const {{ members, skills }} = filteredData();
  let html = '<table><thead><tr>';
  html += '<th style="min-width:80px">氏名</th>';
  skills.forEach(s => {{
    const risk = SKILL_COUNTS[s] <= 2;
    html += `<th class="hm-skill-th${{risk ? ' risk' : ''}}">${{s}}</th>`;
  }});
  html += '</tr></thead><tbody>';

  members.forEach(m => {{
    const info  = MEMBER_INFO[m];
    const color = TEAM_COLORS[info.チーム] || '#888';
    html += `<tr>
      <td class="hm-member-col">
        <span style="display:inline-block;width:8px;height:8px;border-radius:50%;
          background:${{color}};margin-right:6px;vertical-align:middle"></span>${{m}}
        <br><span style="font-size:10px;color:#999;font-weight:400">${{info.役割}}</span>
      </td>`;
    skills.forEach(s => {{
      const has = MATRIX[m][s];
      html += `<td class="hm-cell ${{has ? 'has' : 'none'}}">${{has ? '●' : ''}}</td>`;
    }});
    html += '</tr>';
  }});

  // 保有人数行
  html += '<tr class="hm-count-row"><td class="hm-member-col">保有人数</td>';
  skills.forEach(s => {{
    const cnt  = members.filter(m => MATRIX[m][s]).length;
    const risk = cnt <= 2;
    html += `<td class="${{risk ? 'risk' : ''}}">${{cnt}}</td>`;
  }});
  html += '</tr></tbody></table>';

  document.getElementById('view-area').innerHTML = html;
}}

// ── 表形式 ────────────────────────────────────────────────
function renderTable() {{
  const {{ members, skills }} = filteredData();
  let html = `<table><thead><tr>
    <th>氏名</th><th>役割</th><th>チーム</th><th>スキル</th><th style="text-align:center">保有数</th>
  </tr></thead><tbody>`;

  members.forEach(m => {{
    const info   = MEMBER_INFO[m];
    const color  = TEAM_COLORS[info.チーム] || '#888';
    const owned  = skills.filter(s => MATRIX[m][s]);
    const tags   = owned.map(s => `<span class="skill-tag">${{s}}</span>`).join('');
    html += `<tr>
      <td class="tbl-name">${{m}}</td>
      <td>${{info.役割}}</td>
      <td><span class="tbl-team-badge" style="background:${{color}}">チーム${{info.チーム}}</span></td>
      <td><div class="tbl-skills">${{tags || '<span style="color:#ccc">なし</span>'}}</div></td>
      <td class="tbl-count">${{owned.length}}</td>
    </tr>`;
  }});

  html += '</tbody></table>';
  document.getElementById('view-area').innerHTML = html;
}}
</script>
</body>
</html>"""

    return html

# ── メイン ────────────────────────────────────────────────
def main():
    path = sys.argv[1] if len(sys.argv) > 1 else EXCEL_PATH

    print(f"読み込み中: {path}")
    members, skills = load_excel(path)

    print("データ整形中...")
    member_list, all_skills, matrix, skill_counts, member_info = build_matrix(members, skills)

    print("HTML生成中...")
    html = generate_html(member_list, all_skills, matrix, skill_counts, member_info)

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n出力完了: {OUTPUT_HTML}")
    print(f"  メンバー数: {len(member_list)}人")
    print(f"  スキル種別: {len(all_skills)}種")
    print("\n── スキル偏りリスク（保有2人以下）──")
    for s, cnt in sorted(skill_counts.items(), key=lambda x: x[1]):
        if cnt <= 2:
            print(f"  {s}: {cnt}人")

if __name__ == "__main__":
    main()
