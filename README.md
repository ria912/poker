# Texas Hold'em Web Poker Practice App
holdem_app/
├── backend/
│   ├── main.py
│   │   └─ FastAPI アプリの起動ファイル。ルーティング設定と CORS 設定などを行う。
│
│   ├── api/
│   │   └── endpoints.py
│   │       └─ フロントエンドとのやり取りを担う API エンドポイント群。
│   │          例：/start-hand, /player-action, /get-game-state など。
│
│   ├── core/
│   │   └── game_manager.py
│   │       └─ ゲームのセッション全体を制御。RoundManagerを使って進行を管理する。
│
│   ├── models/
│   │   ├── player.py
│   │   │   └─ プレイヤーの基本クラス（共通の属性：スタック、ハンド、状態など）。
│   │   ├── human_player.py
│   │   │   └─ 人間プレイヤー固有の処理（決定の待機など）。
│   │   ├── ai_player.py
│   │   │   └─ シンプルなAIによるアクション選択ロジック。
│   │   ├── deck.py
│   │   │   └─ トランプの生成・シャッフル・カード配布を担う。
│   │   ├── action.py
│   │   │   └─ fold, call, raise などのアクションルールや適用処理。
│   │   ├── position.py
│   │   │   └─ BTN（ボタン）を起点としたポジションの割り当て・回転ロジック。
│   │   └── round_manager.py
│   │       └─ ラウンド進行管理（プリフロップ、フロップ、ターン、リバー、ショーダウン）。
│
├── frontend/
│   ├── index.html
│   │   └─ メイン画面。プレイヤーの手札やボード、アクションボタンなどを表示。
│
│   ├── js/
│   │   └── app.js
│   │       └─ Alpine.js によるフロントエンドロジック。
│   │          - サーバーからのデータ取得
│   │          - アクション送信
│   │          - UIのリアクティブ更新
│
│   ├── css/
│   │   └── style.css
│   │       └─ Tailwind CSS のカスタマイズや追加スタイルを記述（任意）。
│
├── requirements.txt
│   └─ Python依存パッケージの一覧（例：fastapi, uvicorn, pydantic など）。
│
├── README.md
│   └─ このプロジェクトの概要、構成、起動方法、今後の予定などを記述。
