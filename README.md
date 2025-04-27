# Texas Hold'em Web Poker Practice App

このアプリは、学習・練習用途に最適なシングルプレイヤー向けポーカーアプリです。
Flask + Python をベースに構築され、将来的なオンライン対戦やAI強化にも対応可能な構成になっています。

構成詳細:
---------

1. メインアプリ:
   └── app.py
       - Flaskアプリケーションの起動
       - ルーティング、セッション管理
       - UIとロジックの橋渡し

2. ゲームロジック:
   └── poker_engine.py
       - ゲーム全体の進行（ラウンド・ターン処理）
       - プレイヤーからのアクション受付
       - CPUアクションの処理

3. モデル:
   └── models/
       ├── player.py
       │   - Playerクラス（人間/CPU共通）
       │   - hand, stack, position, folded状態などを管理
       │
       ├── table.py
       │   - Tableクラス
       │   - 現在のベッティングラウンド、アクティブプレイヤー、ポジションローテーションなど
       │
       └── action.py
           - アクションの合法性チェック
           - アクション適用時のスタック更新

4. テンプレート / 静的ファイル:
   ├── templates/ （HTML）
   ├── static/    （Tailwind CSS、JavaScriptなど）

5. テスト:
   └── tests/
       ├── test_player.py
       ├── test_table.py
       └── test_poker_engine.py
           - 単体テスト。pytest対応。
           - 各クラスの挙動・一連のゲームロジックが正しく動作するかを検証。

今後の予定:
------------
- プレイ履歴保存機能（ログ/DB）
- CPUキャラの個性付け (LAG, TAG, ニットなど)
- マルチプレイヤー対応（SocketIO）

実行方法:
----------
1. `python app.py` でサーバ起動
2. ブラウザで `http://localhost:5000` にアクセス
3. UIからゲームをスタート

