function pokerApp() {
  return {
    // --- 状態 ---
    state: {
      round: "",
      pot: 0,
      board: [],
      seats: [],
    },
    isMyTurn: false,
    actionList: [],
    selectedAction: "",
    amount: 0,

    // --- 初期化 ---
    async startGame() {
      try {
        const res = await fetch("/api/game/start", {
          method: "POST",
        });
        const data = await res.json();
        this.updateState(data);
      } catch (err) {
        console.error("ゲーム開始エラー:", err);
      }
    },

    // --- アクション送信 ---
    async submitAction() {
      try {
        const res = await fetch("/api/game/action", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            action: this.selectedAction,
            amount: parseInt(this.amount) || 0,
          }),
        });
        const data = await res.json();
        this.updateState(data);
      } catch (err) {
        console.error("アクション送信エラー:", err);
      }
    },

    // --- ステート更新 ---
    updateState(data) {
      this.state = data.state;
      this.isMyTurn = data.status === "WAITING_FOR_HUMAN";
      this.actionList = data.legal_actions || [];
      this.selectedAction = "";
      this.amount = 0;
    },

    // --- アクション選択 ---
    selectAction(action) {
      this.selectedAction = action;
    },

    // --- Raise / Bet 時だけ金額入力を表示 ---
    get selectedActionRequiresAmount() {
      return ["raise", "bet"].includes(this.selectedAction);
    },

    // --- ボード整形表示 ---
    formatBoard(board) {
      return board.join(" ");
    },
  };
}
