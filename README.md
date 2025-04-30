# Texas Hold'em Web Poker Practice App

models/

- player.py  
  - プレイヤークラスを定義。人間／AIの区別、所持チップ、現在のベット額、フォールド状態などの状態を保持。  
  - reset_for_new_hand() により毎ハンド初期化可能。

- ai_player.py  
  - Player を継承したAIプレイヤー。  
  - 現在は CHECK > CALL > FOLD 優先の非常に簡易な決定ロジックを持つ（テスト用）。

- action.py  
  - ポーカーにおける行動（FOLD, CALL, CHECK, BET, RAISE, ALL-IN）を列挙。  
  - get_legal_actions(): プレイヤーのスタックとテーブル状況から可能な行動一覧を生成。  
  - apply_action(): 行動をテーブルとプレイヤーに適用し、スタックやポットを更新。

- deck.py  
  - トランプデッキを生成・シャッフル・ドローする Deck クラスを定義。

- position.py  
  - ポジションの割り当て順序を管理。  
  - rotate_players(): プレイヤーの並び順を1つ回転（ボタンが移動）。  
  - assign_positions(): 現在のアクティブプレイヤーに対して BTN→SB→BB→... の順でポジションを付与。

- table.py  
  - ゲームテーブルの全体的な状態（プレイヤー、ポット、コミュニティカード、ベット情報など）を管理。  
  - start_hand(): 1ハンドの開始処理を包括（シャッフル、ポジション再設定、ブラインド投稿、配牌など）。

- round_manager.py  
  - ゲームの進行を管理する中心クラス。  
  - 各フェーズ（preflop, flop, turn, river, showdown）を順に進めるロジックを含む。  
  - proceed_action(): 現在のプレイヤーに行動させる。  
  - advance_phase(): フェーズが進行し、必要に応じてカードが公開される。  
  - handle_showdown(): 勝者をランダムに決定してポットを渡す（暫定実装）。


💡 今後の拡張ポイント

- showdown の判定ロジック（ハンド強さの比較）を実装  
- AIプレイヤーに戦略を追加  
- UIとの接続（Flask, Reactなど）による操作性向上  
- プレイ履歴の保存と表示機能