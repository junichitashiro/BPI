"""
サプライヤーチーム相関図ジェネレーター
--------------------------------------
Excelファイル（メンバー / スキル / 業務フロー の3シート）を読み込み、
networkxで中心性分析を行い、pyvisでインタラクティブなHTMLを出力する。
"""

import pandas as pd
import networkx as nx
from pyvis.network import Network
import sys

# ── 設定 ────────────────────────────────────────────────
EXCEL_PATH  = "team.xlsx"
OUTPUT_HTML = "team_graph.html"

# チームカラー（pyvisはHTMLカラーコードで指定）
TEAM_COLORS = {
    "A": "#5B8CF0",   # blue
    "B": "#E8773A",   # coral
}
# ── Excelを読み込む ──────────────────────────────────────
def load_excel(path: str):
    members = pd.read_excel(path, sheet_name="メンバー")
    skills  = pd.read_excel(path, sheet_name="スキル")
    flows   = pd.read_excel(path, sheet_name="業務フロー")
    return members, skills, flows

# ── グラフ構築 ────────────────────────────────────────────
def build_graph(members, skills, flows):
    G = nx.DiGraph()

    # スキルを人物ごとにまとめてノード属性として持つ
    skill_map = skills.groupby("氏名")["スキル"].apply(list).to_dict()

    # 人物ノード
    for _, row in members.iterrows():
        name = row["氏名"]
        G.add_node(
            name,
            node_type="person",
            role=row["役割"],
            team=row["チーム"],
            skills=skill_map.get(name, []),
        )

    # 業務フローエッジ
    for _, row in flows.iterrows():
        G.add_edge(
            row["送り手"], row["受け手"],
            edge_type="flow",
            label=row["業務内容"],
        )

    return G

# ── 中心性分析 ────────────────────────────────────────────
def compute_centrality(G):
    # 業務フローのみの部分グラフで計算
    flow_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get("edge_type") == "flow"]
    G_flow = G.edge_subgraph(flow_edges).copy()

    bc = nx.betweenness_centrality(G_flow)   # ボトルネック検出
    dc = nx.in_degree_centrality(G_flow)     # 情報集中度

    return bc, dc

# ── pyvis ネットワーク構築 ─────────────────────────────────
def build_pyvis(G, betweenness, in_degree, members):
    net = Network(
        height="720px",
        width="100%",
        directed=True,
        bgcolor="#f8f7f4",
    )
    net.barnes_hut(
        gravity=-12000,
        central_gravity=0.2,
        spring_length=260,
        spring_strength=0.03,
        damping=0.12,
        overlap=1,
    )
    net.set_options("""
    {
      "nodes": {
        "font": {
          "color": "#ffffff"
        }
      }
    }
    """)

    for node, data in G.nodes(data=True):
        if data.get("node_type") == "person":
            team  = data.get("team", "?")
            role  = data.get("role", "")
            bc    = betweenness.get(node, 0)
            idc   = in_degree.get(node, 0)
            # ボトルネック候補は赤枠で強調
            border_color = "#E82C2C" if bc > 0.2 else "#ffffff"
            border_width = 4 if bc > 0.2 else 1.5

            color = TEAM_COLORS.get(team, "#888")

            skill_list = data.get("skills", [])
            skill_str  = "、".join(skill_list) if skill_list else "なし"
            tooltip_lines = [
                f"役割: {role}",
                f"スキル: {skill_str}",
                f"媒介中心性: {bc:.3f}",
                f"情報集中度: {idc:.3f}",
            ]
            if bc > 0.2:
                tooltip_lines.append("⚠ ボトルネック候補")
            tooltip = "\n".join(tooltip_lines)

            net.add_node(
                node,
                label=node,
                color=color,
                borderWidth=border_width,
                title=tooltip,
                font={"size": 13, "color": "#ffffff", "bold": True},
                shape="circle",
                margin=10,
            )
            # ボーダーカラーはoptions経由で上書き（pyvisの型制約を回避）
            net.node_map[node]["color"] = {
                "background": color,
                "border": border_color,
                "highlight": {"background": color, "border": "#FFD700"},
            }

    for src, dst, data in G.edges(data=True):
        if data.get("edge_type") == "flow":
            net.add_edge(
                src, dst,
                title=data.get("label", ""),
                label=data.get("label", ""),
                color={"color": "#888880", "highlight": "#333"},
                width=1.5,
                arrows="to",
                font={"size": 9, "color": "#666"},
                smooth={"type": "curvedCW", "roundness": 0.15},
            )
    return net

# ── HTML出力（凡例・フィルターUI付き）─────────────────────
def inject_ui(html_path: str, betweenness: dict):
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    # ボトルネックサマリー
    top_bn = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)[:3]
    bn_rows = "".join(
        f"<tr><td style='padding:2px 8px'>{n}</td>"
        f"<td style='padding:2px 8px;color:{'#E82C2C' if s>0.2 else '#444'}'>"
        f"{'⚠ ' if s>0.2 else ''}{s:.3f}</td></tr>"
        for n, s in top_bn
    )

    legend_html = f"""
<div id="legend" style="
  position:fixed; top:16px; right:16px; z-index:999;
  background:#fff; border:1px solid #ddd; border-radius:10px;
  padding:14px 18px; font-family:sans-serif; font-size:12px;
  box-shadow:0 2px 8px rgba(0,0,0,0.12); min-width:200px;">
  <div style="font-weight:600;margin-bottom:8px;font-size:13px">凡例 &amp; 分析</div>
  <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">
    <span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:#5B8CF0"></span>チームA
  </div>
  <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">
    <span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:#E8773A"></span>チームB
  </div>
  <div style="display:flex;align-items:center;gap:6px;margin-bottom:10px">
    <span style="display:inline-block;width:14px;height:14px;border-radius:50%;background:transparent;border:3px solid #E82C2C"></span>ボトルネック候補（赤枠）
  </div>
  <hr style="border:none;border-top:1px solid #eee;margin:8px 0">
  <div style="font-weight:600;margin-bottom:6px">媒介中心性 TOP3</div>
  <table style="border-collapse:collapse">
    {bn_rows}
  </table>
  <hr style="border:none;border-top:1px solid #eee;margin:8px 0">
  <div style="color:#888;font-size:10px">赤枠＝ボトルネック候補（>0.2）<br>ノードをホバーでスキル・詳細表示</div>
</div>
"""

    html = html.replace("</body>", legend_html + "</body>")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

# ── メイン ────────────────────────────────────────────────
def main():
    path = sys.argv[1] if len(sys.argv) > 1 else EXCEL_PATH

    print(f"読み込み中: {path}")
    members, skills, flows = load_excel(path)

    print("グラフ構築中...")
    G = build_graph(members, skills, flows)

    print("中心性分析中...")
    bc, idc = compute_centrality(G)

    print("可視化生成中...")
    net = build_pyvis(G, bc, idc, members)
    net.save_graph(OUTPUT_HTML)

    inject_ui(OUTPUT_HTML, bc)

    print(f"\n出力完了: {OUTPUT_HTML}")
    print("\n── 媒介中心性（ボトルネック分析）──")
    for name, score in sorted(bc.items(), key=lambda x: x[1], reverse=True):
        flag = " ← ⚠ ボトルネック候補" if score > 0.2 else ""
        print(f"  {name:8s}: {score:.3f}{flag}")

if __name__ == "__main__":
    main()
