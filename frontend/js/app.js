function gameApp() {
    return {
        game: {},
        async init() {
            const res = await fetch('http://localhost:8000/game/state');
            this.game = await res.json();
        }
    }
}
