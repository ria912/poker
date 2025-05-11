// frontend/js/app.js
function pokerApp() {
    return {
        tableState: null,
        humanPlayer: null,

        async init() {
            await this.fetchState();
        },

        async startGame() {
            const res = await fetch("/api/start", { method: "POST" });
            const data = await res.json();
            this.tableState = data.state;
            this.updateHuman();
            this.pollAI();
        },

        async fetchState() {
            const res = await fetch("/api/state");
            const data = await res.json();
            this.tableState = data;
            this.updateHuman();
        },

        updateHuman() {
            if (!this.tableState) return;
            this.humanPlayer = this.tableState.players.find(p => p && p.name === "YOU");
        },

        async sendAction(action, amount = 0) {
            const res = await fetch("/api/action", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ action, amount }),
            });
            const data = await res.json();
            this.tableState = data.state;
            this.updateHuman();

            // AIの行動をポーリングで進行
            this.pollAI();
        },

        async pollAI() {
            // 少し遅延を置いてAIが複数回アクションするようにする
            const checkAI = async () => {
                await this.fetchState();
                const stillAIPlaying = this.tableState.players.some(
                    p => p && p.name !== "YOU" && !p.has_folded
                );
                if (stillAIPlaying) {
                    await new Promise(r => setTimeout(r, 1000));
                    await checkAI();
                }
            };
            checkAI();
        }
    };
}
