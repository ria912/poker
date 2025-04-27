from flask import Flask, render_template, session, redirect, url_for
from poker_engine import PokerGame

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game')
def game():
    # 新しいゲームセッションを初期化
    session['game'] = PokerGame().to_dict()
    return render_template('game.html')

if __name__ == '__main__':
    app.run(debug=True)
