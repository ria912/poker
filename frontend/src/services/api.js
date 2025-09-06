// src/services/api.js
const API_BASE_URL = 'http://localhost:8000'; // 実際のアプリでは環境変数を使用します

const request = async (endpoint, options = {}) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
        ...options,
    };

    try {
        const response = await fetch(url, config);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'APIエラーが発生しました');
        }
        return response.json();
    } catch (err) {
        console.error("API request failed:", err);
        throw err;
    }
};

export const api = {
    createGame: (data) => request('/games', { method: 'POST', body: JSON.stringify(data) }),
    getGameState: (gameId) => request(`/games/${gameId}`),
    postAction: (gameId, action) => request(`/games/${gameId}/action`, { method: 'POST', body: JSON.stringify(action) }),
    nextHand: (gameId) => request(`/games/${gameId}/next_hand`, { method: 'POST' })
};