from flask import Flask, render_template, request, jsonify
from poker_engine import PokerEngine

app = Flask(__name__)

engine = PokerEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_game', methods=['POST'])
def start_game():
    player_name = request.form['player_name']
    engine.start_game()
    return render_template('game.html', phase=engine.round_manager.phase, pot=engine.table.pot, hand=["X", "X"], stack=10000, legal_actions=["bet", "call", "raise", "fold"], game_info="ゲームを始めます！")

@app.route('/action/<action>', methods=['POST'])
def action(action):
    data = request.get_json()
    amount = int(data['amount']) if 'amount' in data else 0
    # プレイヤーアクションの処理
    player = engine.table.players[0]  # 仮にプレイヤー1を使用
    Action.apply_action(player, action, engine.table, amount)
    
    # ゲーム進行の更新
    engine.round_manager.proceed_round()
    
    # 状態を更新して返す
    return jsonify({
        'success': True,
        'game_state': f"現在のラウンド: {engine.round_manager.phase}, ポット: ¥{engine.table.pot}"
    })

if __name__ == '__main__':
    app.run(debug=True)
