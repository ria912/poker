function pokerApp() {
  return {
    statusMessage: 'ゲームを開始してください。',
    isMyTurn: false,
    actionList: [],
    selectedAction: null,
    amount: 0,

    async startGame() {
      try {
        const res = await fetch('/api/game/start', {
          method: 'POST'
        });
        const data = await res.json();
        this.updateState(data.state || data); // サーバーの返却形式に対応
      } catch (e) {
        this.statusMessage = 'ゲーム開始時にエラーが発生しました。';
        console.error(e);
      }
    },

    async sendAction() {
      try {
        const res = await fetch('/api/game/action', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            action: this.selectedAction,
            amount: this.amount
          })
        });

        const data = await res.json();
        this.selectedAction = null;
        this.amount = 0;
        this.updateState(data.state || data); // サーバーの返却形式に対応
      } catch (e) {
        this.statusMessage = 'アクション送信時にエラーが発生しました。';
        console.error(e);
      }
    },

    async fetchState() {
      try {
        const res = await fetch('/api/game/state');
        const data = await res.json();
        this.updateState(data);
      } catch (e) {
        this.statusMessage = '状態の取得に失敗しました。';
        console.error(e);
      }
    },

    updateState(data) {
      // サーバーの返却形式に合わせて値を抽出
      this.statusMessage = this.formatStatus(data);
      // valid_actionsがなければ推測して生成
      if (data.valid_actions) {
        this.actionList = data.valid_actions;
      } else if (data.seats) {
        // 現在の人間プレイヤーを特定し、アクション候補を推測
        const me = (data.seats || []).find(p => p && p.is_human && !p.has_left);
        if (me && me.legal_actions) {
          this.actionList = me.legal_actions.map(a => ({ name: a }));
        } else {
          this.actionList = [];
        }
      } else {
        this.actionList = [];
      }
      this.isMyTurn = data.waiting_for_human === true;
    },

    formatStatus(data) {
      let s = `Pot: ${data.pot}\n`;
      s += `Board: ${data.board?.join(' ') || '---'}\n`;
      s += `Players:\n`;

      // プレイヤーリストの取得方法を seats/players 両対応
      const players = data.players || data.seats || [];
      for (const p of players) {
        if (!p) continue;
        const hand = p.hand?.join(' ') || '?? ??';
        s += ` - ${p.name} (${p.stack}) ${p.has_folded ? '[FOLD]' : ''}`;
        if (p.is_human) s += ' ← YOU';
        if (p.hand) s += ` | Hand: ${hand}`;
        s += '\n';
      }

      s += `\nTurn: ${data.current_player_name || ''}`;
      return s;
    },

    selectAction(name) {
      this.selectedAction = name;
      this.amount = 0;
    },

    get selectedActionRequiresAmount() {
      return this.selectedAction === 'raise' || this.selectedAction === 'bet';
    }
  };
}