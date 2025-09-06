// src/App.jsx
import React from 'react';
import {
    Paper,
    CircularProgress,
    Alert,
    Box,
    ThemeProvider,
    CssBaseline,
} from '@mui/material';
import { darkTheme } from './theme';
import { useGame } from './hooks/useGame';

// コンポーネントをインポート
import NewGameForm from './components/NewGameForm';
import GameTable from './components/GameTable';
import PlayerActions from './components/PlayerActions';
import GameLog from './components/GameLog';

function App() {
    const {
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
    } = useGame();

    return (
        <ThemeProvider theme={darkTheme}>
            <CssBaseline />
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', bgcolor: '#000' }}>
                <Paper elevation={12} sx={{ width: '100%', maxWidth: 450, height: '95vh', maxHeight: 900, borderRadius: { sm: '24px' }, overflow: 'hidden', display: 'flex', flexDirection: 'column', bgcolor: 'background.default' }}>
                    <Box sx={{ p: 1, flexShrink: 0, bgcolor: 'rgba(0,0,0,0.2)'}}>
                       {gameState && <GameLog actions={logHistory} />}
                    </Box>

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
                                gameStatus={gameState.status}
                                currentRound={gameState.current_round}
                            />
                        )}
                    </Box>

                    {humanPlayer && gameState && (
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