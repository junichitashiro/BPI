# KousakuMap

機械加工現場の作業者スキルをヒートマップで可視化するブラウザツールです。
Claude のスキル `machining-skill-interview` によるヒアリング結果（JSONファイル）を読み込み、加工者ごとのスキル分布を一覧表示します。

---

## 特徴

- JSONファイルが入ったフォルダを選択するだけで即座に表示
- 7カテゴリのタブ切り替えでスキルを分類表示
- スコア 0〜5 を濃淡カラーで直感的に可視化
- サーバー不要・インストール不要（HTMLファイル単体で動作）

---

## 必要環境

| 項目 | 要件 |
|---|---|
| ブラウザ | Chrome または Edge（最新版推奨） |
| サーバー | 不要 |
| インストール | 不要 |

> Firefox は File System Access API に非対応のため動作しません。

---

## ファイル構成

```
KousakuMap/
├── kousakumap.html       # ツール本体
└── data/                 # JSONファイルの格納フォルダ（任意の名前でよい）
    ├── 鈴木_20260612.json
    ├── 田中_20260601.json
    └── ...
```

---

## 使い方

1. `kousakumap.html` をブラウザで開く
2. 「フォルダを選択して読み込む」ボタンをクリック
3. JSONファイルが入ったフォルダを選択する
4. ヒートマップが表示される
5. 上部のカテゴリタブでスキルカテゴリを切り替える

---

## JSONファイルの仕様

### 命名規則

```
名前_実施年月日.json
例：鈴木_20260612.json
```

ファイル名の「名前」部分がヒートマップ上の加工者表示名になります。日本語・ローマ字どちらも使用できます。

### フォーマット

`machining-skill-interview` スキルが出力する `operators.json` 形式に準拠します。

```json
{
  "operators": [
    {
      "id": "OP-01",
      "name": "鈴木",
      "level": "エキスパート",
      "experience_years": 0,
      "scores": {
        "nc_lathe": 5,
        "manual_lathe": 3,
        "mc_vertical": 0,
        "mc_multi": 5,
        "milling": 0,
        "surface_grind": 0,
        "cylindrical_grind": 0,
        "edm": 0,
        "g_code": 0,
        "dialog_program": 4,
        "cam": 3,
        "program_debug": 4,
        "drawing": 5,
        "gd_t": 5,
        "material": 5,
        "measurement_basic": 5,
        "cmm": 2,
        "inspection": 5,
        "quality_kaizen": 4,
        "cert_lathe": 0,
        "cert_nc": 0,
        "cert_mc": 0,
        "cert_maintenance": 0,
        "cert_other": 0,
        "setup": 5,
        "multi_process": 4,
        "sop": 3,
        "teaching": 4,
        "teaching_trainee": 0,
        "kaizen": 5,
        "digital": 0
      },
      "notes": "総合コメント"
    }
  ]
}
```

### スコアキー一覧

| カテゴリ | キー | 説明 |
|---|---|---|
| 機械操作 | `nc_lathe` | NC旋盤 |
| | `manual_lathe` | 普通旋盤 |
| | `mc_vertical` | マシニングセンタ（立型） |
| | `mc_multi` | マシニングセンタ（横型・5軸） |
| | `milling` | フライス盤 |
| | `surface_grind` | 平面研削盤 |
| | `cylindrical_grind` | 円筒・内面研削盤 |
| | `edm` | ワイヤ・形彫放電加工機 |
| NCプログラム・CAM | `g_code` | Gコード手書き |
| | `dialog_program` | 対話式プログラム |
| | `cam` | CAM操作 |
| | `program_debug` | プログラム修正・デバッグ |
| 図面・公差 | `drawing` | 図面読み取り |
| | `gd_t` | 幾何公差 |
| | `material` | 材料特性 |
| 計測・品質 | `measurement_basic` | 汎用計測器 |
| | `cmm` | 三次元測定機 |
| | `inspection` | 工程内検査 |
| | `quality_kaizen` | 不良原因分析 |
| 資格 | `cert_lathe` | 技能士（旋盤）|
| | `cert_nc` | 技能士（NC旋盤）|
| | `cert_mc` | 技能士（マシニングセンタ）|
| | `cert_maintenance` | 機械保全技能士 |
| | `cert_other` | その他資格 |
| 段取り・工程管理 | `setup` | 段取り替え |
| | `multi_process` | 多品種・複数機管理 |
| | `sop` | 作業標準書作成 |
| 指導・改善 | `teaching` | 後輩指導（日本人） |
| | `teaching_trainee` | 技能実習生指導 |
| | `kaizen` | 工程改善提案 |
| | `digital` | デジタルツール活用 |

---

## スコア基準

| スコア | 意味 |
|---|---|
| 0 | 経験なし |
| 1 | 見学・補助のみ |
| 2 | 指示のもとで単独作業可 |
| 3 | 段取りから加工まで自立 |
| 4 | 難易度の高い仕事・複数機種に対応可 |
| 5 | 社内の第一人者レベル |

---

## レベル判定

加工スキル系キーの平均（未経験項目を除く）をもとに自動算出されます。

| 平均スコア | レベル |
|---|---|
| 0.0〜1.9 | 初級 |
| 2.0〜3.4 | 中級 |
| 3.5〜4.4 | 熟練 |
| 4.5〜5.0 | エキスパート |

---

## 関連

このツールは Claude スキル `machining-skill-interview` と連携して使用します。ヒアリングから JSON 出力、KousakuMap での可視化までが一連のワークフローです。
