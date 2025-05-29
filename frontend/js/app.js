function pokerApp() {
  return {
    state: {
      round: '',
      pot: 0,
      board: [],
      seats: []
    },
    isMyTurn: false,
    actionList: [],
    selectedAction: '',
    amount: null,

    startGame() {
      fetch("/api/game/start", { method: "POST" })
        .then(() => this.fetchState());
    },

    fetchState() {
      fetch("/api/game/state")
        .then(res => res.json())
        .then(data => this.updateState(data));
    },

    updateState(data) {
      this.state = data;
      const human = data.seats.find(p => p && p.is_human);
      this.isMyTurn = human?.is_turn || false;
      this.actionList = human?.legal_actions || [];
    },

    selectAction(actionName) {
      this.selectedAction = actionName;
      if (!this.selectedActionRequiresAmount) {
        this.submitAction(actionName);
      }
    },

    submitAction(actionName) {
      const payload = { name: actionName };
      if (['raise', 'bet'].includes(actionName)) {
        payload.amount = this.amount;
      }

      fetch("/api/game/action", {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      }).then(() => {
        this.amount = null;
        this.selectedAction = '';
        this.fetchState();
      });
    },

    formatBoard(board) {
      return board && board.length ? board.join(" ") : "なし";
    },

    seatPositionClass(seatNumber) {
      const positions = {
        1: "top-0 left-1/2 -translate-x-1/2",
        2: "top-1/4 right-0",
        3: "bottom-1/4 right-0",
        4: "bottom-0 left-1/2 -translate-x-1/2",
        5: "bottom-1/4 left-0",
        6: "top-1/4 left-0"
      };
      return positions[seatNumber] || "";
    },

    get selectedActionRequiresAmount() {
      return ['raise', 'bet'].includes(this.selectedAction);
    }
  };
}
