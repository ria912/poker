import React, { useState, useEffect } from 'react';
import {
    Paper,
    CircularProgress,
    Alert,
    Box,
    ThemeProvider,
    createTheme,
    CssBaseline
} from '@mui/material';
import GameTable from './components/GameTable.jsx';
import PlayerActions from './components/PlayerActions.jsx';
import GameLog from './components/GameLog.jsx';
import NewGameForm from './components/NewGameForm.jsx';
import api from './services/api.js';

// アプリケーション全体に適用するダークテーマを定義
const darkTheme = createTheme({
    palette: {
        mode: 'dark',
        background: {
            default: '#121212',
            paper: '#1e1e1e',
        },
        primary: {
            main: '#f0a500', // Gold/Amber color for accents
        },
        secondary: {
            main: '#4caf50',
        },
    },
    typography: {
        fontFamily: 'Roboto, sans-serif',
    },
});

function App() {
    const [gameState, setGameState] = useState(null);
    const [gameId, setGameId] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [humanPlayer, setHumanPlayer] = useState(null);
    const [logHistory, setLogHistory] = useState([]);

    useEffect(() => {
        if (gameState) {
            const human = gameState.seats.find(s => s.player && !s.player.is_ai);
            setHumanPlayer(human);
            // 新しいハンドが始まったらログをリセット
            if (gameState.last_message.includes('New hand started')) {
                setLogHistory([gameState.last_message]);
            } else {
                // 既存のログに新しいメッセージを追加（重複は避ける）
                setLogHistory(prev => {
                    const newActions = gameState.last_message.trim().split('.').filter(Boolean);
                    const lastActionInHistory = prev.join('.').trim().split('.').filter(Boolean).pop();
                     // 新しいアクションのみを追加
                    const uniqueNewActions = newActions.filter(action => !prev.join('.').includes(action));
                    return [...prev, ...uniqueNewActions.map(a => a.trim() + '.')];
                });
            }
        }
    }, [gameState]);

    const handleNewGame = async (players) => {
        setLoading(true);
        setError('');
        setLogHistory([]); // 新しいゲームでログをクリア
        try {
            const data = await api.createGame({ players });
            setGameState(data);
            setGameId(data.game_id);
        } catch (err) {
            setError(err.message || 'Failed to start a new game.');
        } finally {
            setLoading(false);
        }
    };

    const handlePlayerAction = async (action) => {
        if (!gameId || !humanPlayer) return;
        setLoading(true);
        setError('');
        try {
            const payload = {
                player_id: humanPlayer.player.player_id,
                action_type: action.type,
                amount: action.amount,
            };
            const data = await api.postAction(gameId, payload);
            setGameState(data);
        } catch (err) {
            setError(err.message || 'Action failed.');
        } finally {
            setLoading(false);
        }
    };

    const handleNextHand = async () => {
        if (!gameId) return;
        setLoading(true);
        setError('');
        setLogHistory([]); // 次のハンドでログをクリア
        try {
            const data = await api.nextHand(gameId);
            setGameState(data);
        } catch (err) {
            setError(err.message || 'Failed to start next hand.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <ThemeProvider theme={darkTheme}>
            <CssBaseline />
            {/* ページ全体の背景と、中央寄せのためのコンテナ */}
            <Box sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                minHeight: '100vh',
                bgcolor: '#000'
            }}>
                {/* スマートフォン風の表示フレーム */}
                <Paper elevation={12} sx={{
                    width: '100%',
                    maxWidth: 450,
                    height: '95vh',
                    maxHeight: 900,
                    borderRadius: { sm: '24px' },
                    overflow: 'hidden',
                    display: 'flex',
                    flexDirection: 'column',
                    bgcolor: 'background.default'
                }}>

                    {/* 上部: ゲームログ */}
                    <Box sx={{ p: 1, flexShrink: 0, bgcolor: 'rgba(0,0,0,0.2)'}}>
                       {/* logHistoryを結合して渡す */}
                       {gameState && <GameLog message={logHistory.join(' ')} />}
                    </Box>

                    {/* 中央: ゲームテーブル or フォーム */}
                    <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
                        {error && <Alert severity="error" onClose={() => setError('')} sx={{position: 'absolute', top: 20, zIndex: 10, left: 20, right: 20}}>{error}</Alert>}

                        {!gameId ? (
                            <Box sx={{p: 4, width: '100%'}}>
                                <NewGameForm onNewGame={handleNewGame} loading={loading} />
                            </Box>
                        ) : !gameState ? (
                            <CircularProgress />
                        ) : (
                            <GameTable
                                seats={gameState.seats}
                                communityCards={gameState.community_cards}
                                pot={gameState.pot}
                                currentSeatIndex={gameState.current_seat_index}
                                dealerSeatIndex={gameState.dealer_seat_index}
                            />
                        )}
                    </Box>

                    {/* 下部: プレイヤーのアクション */}
                    {humanPlayer && (
                        <Box sx={{ p: 2, flexShrink: 0, bgcolor: 'rgba(0,0,0,0.2)' }}>
                            <PlayerActions
                                validActions={gameState.valid_actions}
                                onAction={handlePlayerAction}
                                onNextHand={handleNextHand}
                                gameStatus={gameState.status}
                                loading={loading}
                            />
                        </Box>
                    )}

                </Paper>
            </Box>
        </ThemeProvider>
    );
}

export default App;

