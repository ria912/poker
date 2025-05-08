# Texas Hold'em Web Poker Practice App
holdem_app/
├── backend/
│   ├── models/
│   │   ├── player.py
│   │   │   └─ プレイヤーの基本クラス（名前、スタック、ハンド、状態などの共通属性を管理）
│   │   ├── human_player.py
│   │   │   └─ 人間プレイヤー固有のロジック（入力を待ってアクションを決定）
│   │   ├── ai_player.py
│   │   │   └─ シンプルなAIによるアクション選択（チェック → コール → フォールドの優先順位）
│   │   ├── deck.py
│   │   │   └─ トランプの生成、シャッフル、カードのドロー（山札管理）
│   │   ├── action.py
│   │   │   └─ fold / call / raise などのアクション定義、合法手の判定、アクション適用処理
│   │   ├── position.py
│   │   │   └─ BTN（ボタン）を起点にしたポジションの割り当てとローテーション（SB, BB, COなど）
│   │   └── round_manager.py
│   │       └─ 各ストリートの進行、アクション順序、ベッティングラウンド、ショーダウン処理
│
├── tests/
│   └── test_run.py
│       └─ 自動プレイヤー（AutoHumanPlayer, AI）を使った1ゲーム通しのラウンド進行テスト
