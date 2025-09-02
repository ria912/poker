// src/services/api.js
const API_BASE_URL = 'http://localhost:8000'; // FastAPIサーバーのURL

const request = async (endpoint, options = {}) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers,
        },
        ...options,
    };

    const response = await fetch(url, config);
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'An API error occurred');
    }
    return response.json();
};

const api = {
    createGame: (data) => {
        return request('/games', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },
    getGameState: (gameId) => {
        return request(`/games/${gameId}`);
    },
    postAction: (gameId, action) => {
        return request(`/games/${gameId}/action`, {
            method: 'POST',
            body: JSON.stringify(action),
        });
    },
    nextHand: (gameId) => {
         return request(`/games/${gameId}/next_hand`, {
            method: 'POST',
        });
    }
};

export default api;