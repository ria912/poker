// src/hooks/useGame.js
import { useState, useEffect } from 'react';
import { api } from '../services/api';

export const useGame = () => {
    const [gameState, setGameState] = useState(null);
    const [gameId, setGameId] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [humanPlayer, setHumanPlayer] = useState(null);
    const [logHistory, setLogHistory] = useState([]);

    useEffect(() => {
        if (gameState) {
            setHumanPlayer(gameState.seats.find(s => s.player && !s.player.is_ai));
            if (gameState.log_messages && gameState.log_messages.length > 0) {
                // 新しいハンドが始まったらログをリセット、そうでなければ追記
                if (gameState.log_messages.some(msg => msg.includes('New hand started') || msg.includes('Started next hand'))) {
                    setLogHistory(gameState.log_messages);
                } else {
                    setLogHistory(prev => [...new Set([...prev, ...gameState.log_messages])]);
                }
            }
        }
    }, [gameState]);

    const handleApiCall = async (apiFunc, ...args) => {
        setLoading(true);
        setError('');
        try {
            const data = await apiFunc(...args);
            setGameState(data);
            if (data.game_id) setGameId(data.game_id);
        } catch (err) {
            setError(err.message || '予期せぬエラーが発生しました');
        } finally {
            setLoading(false);
        }
    };

    const handleNewGame = (players) => {
        setLogHistory([]);
        handleApiCall(api.createGame, { players });
    };

    const handlePlayerAction = (action) => {
        if (!gameId || !humanPlayer) return;
        const payload = { player_id: humanPlayer.player.player_id, action_type: action.type, amount: action.amount };
        handleApiCall(api.postAction, gameId, payload);
    };

    const handleNextHand = () => {
        if (!gameId) return;
        // 次のハンドの前にログをクリア
        setLogHistory([]);
        handleApiCall(api.nextHand, gameId);
    };

    return {
        gameState,
        gameId,
        loading,
        error,
        humanPlayer,
        logHistory,
        setError,
        handleNewGame,
        handlePlayerAction,
        handleNextHand,
    };
};