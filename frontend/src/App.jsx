// src/App.js
import React, { useState, useEffect } from 'react';
import { Container, Typography, CircularProgress, Alert, Box, Paper } from '@mui/material';
import GameTable from './components/GameTable';
import PlayerActions from './components/PlayerActions';
import GameLog from './components/GameLog';
import NewGameForm from './components/NewGameForm';
import api from './services/api';

function App() {
    const [gameState, setGameState] = useState(null);
    const [gameId, setGameId] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [humanPlayer, setHumanPlayer] = useState(null);

    // gameStateが更新されたら、人間プレイヤーの情報を更新する
    useEffect(() => {
        if (gameState) {
            const human = gameState.seats.find(s => s.player && !s.player.is_ai);
            setHumanPlayer(human);
        }
    }, [gameState]);

    const handleNewGame = async (players) => {
        setLoading(true);
        setError('');
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
        try {
            const data = await api.nextHand(gameId);
            setGameState(data);
        } catch(err) {
             setError(err.message || 'Failed to start next hand.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <Container maxWidth="lg" sx={{ bgcolor: '#3d3d3d', color: 'white', minHeight: '100vh', py: 4 }}>
            <Typography variant="h3" align="center" gutterBottom sx={{ fontFamily: 'Georgia, serif', fontWeight: 'bold' }}>
                Texas Hold'em AI Battle
            </Typography>

            {error && <Alert severity="error" onClose={() => setError('')}>{error}</Alert>}
            
            {!gameId ? (
                <NewGameForm onNewGame={handleNewGame} loading={loading} />
            ) : !gameState ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
                    <CircularProgress />
                </Box>
            ) : (
                <Paper elevation={3} sx={{ bgcolor: '#006400', p: 3, borderRadius: '150px' }}>
                    <GameTable
                        seats={gameState.seats}
                        communityCards={gameState.community_cards}
                        pot={gameState.pot}
                        currentSeatIndex={gameState.current_seat_index}
                    />
                </Paper>
            )}

            {gameState && (
                <Box sx={{ mt: 4, display: 'flex', gap: 2, justifyContent: 'center' }}>
                    <Box sx={{ width: '60%' }}>
                         {humanPlayer && (
                            <PlayerActions
                                validActions={gameState.valid_actions}
                                onAction={handlePlayerAction}
                                onNextHand={handleNextHand}
                                playerStack={humanPlayer.stack}
                                currentBet={humanPlayer.current_bet}
                                amountToCall={gameState.amount_to_call}
                                gameStatus={gameState.status}
                                loading={loading}
                            />
                        )}
                    </Box>
                    <Box sx={{ width: '40%' }}>
                        <GameLog message={gameState.last_message} />
                    </Box>
                </Box>
            )}
        </Container>
    );
}

export default App;