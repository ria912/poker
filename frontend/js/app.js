// frontend/js/app.js
function pokerApp() {
    const API_BASE = `${location.origin}/api`;  // 開発・本番両対応
    return {
        tableState: null,
        humanPlayer: null,
        isActing: false,

        async init() {
            await this.fetchState();
        },

        async startGame() {
            try {
                const res = await fetch(`${API_BASE}/start`, { method: "POST" });
                if (!res.ok) throw new Error("startGame: API error");
                const data = await res.json();
                this.tableState = data.state;
                this.updateHuman();
                this.pollAI();
            } catch (error) {
                console.error("ゲーム開始エラー:", error);
            }
        },

        async fetchState() {
            try {
                const res = await fetch(`${API_BASE}/state`);
                if (!res.ok) throw new Error("fetchState: API error");
                const data = await res.json();
                this.tableState = data;
                this.updateHuman();
            } catch (error) {
                console.error("状態取得エラー:", error);
            }
        },

        updateHuman() {
            if (!this.tableState) return;
            this.humanPlayer = this.tableState.players.find(
                p => p && p.name === "YOU"
            );
        },

        async sendAction(action, amount = 0) {
            if (this.isActing) return;
            this.isActing = true;
            try {
                const res = await fetch(`${API_BASE}/action`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ action, amount }),
                });
                if (!res.ok) throw new Error("sendAction: API error");
                const data = await res.json();
                this.tableState = data.state;
                this.updateHuman();
                this.pollAI();
            } catch (error) {
                console.error("アクション送信エラー:", error);
            } finally {
                this.isActing = false;
            }
        },

        async pollAI() {
            let aiStillPlaying = true;
            while (aiStillPlaying) {
                await new Promise(r => setTimeout(r, 1000)); // AIの“思考時間”
                await this.fetchState();
                console.log("AIプレイヤー状態チェック:", this.tableState.players);
                aiStillPlaying = this.tableState.players.some(
                    p =>
                        p &&
                        p.name !== "YOU" &&
                        !p.has_folded &&
                        (p.last_action === null || p.last_action === "-")
                );
            }
        }
    };
}

window.pokerApp = pokerApp;