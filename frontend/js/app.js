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
        this.updateState(data);
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
        this.updateState(data);
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
      this.statusMessage = this.formatStatus(data);
      this.actionList = data.valid_actions || [];
      this.isMyTurn = data.waiting_for_human === true;
    },

    formatStatus(data) {
      let s = `Pot: ${data.pot}\n`;
      s += `Board: ${data.board?.join(' ') || '---'}\n`;
      s += `Players:\n`;

      for (const p of data.players) {
        const hand = p.hand?.join(' ') || '?? ??';
        s += ` - ${p.name} (${p.stack}) ${p.folded ? '[FOLD]' : ''}`;
        if (p.is_human) s += ' ← YOU';
        if (p.hand) s += ` | Hand: ${hand}`;
        s += '\n';
      }

      s += `\nTurn: ${data.current_player_name}`;
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