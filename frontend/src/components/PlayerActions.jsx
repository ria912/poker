// src/components/PlayerActions.jsx
import React, { useState, useEffect } from 'react';
import { Box, Button, Slider, Typography, Paper } from '@mui/material';

const PlayerActions = ({ validActions, onAction, onNextHand, gameStatus, loading }) => {
    const [raiseAmount, setRaiseAmount] = useState(0);
    const betOrRaiseInfo = validActions?.find(a => a.type === 'RAISE' || a.type === 'BET');

    useEffect(() => {
        if (betOrRaiseInfo) {
            setRaiseAmount(betOrRaiseInfo.min);
        }
    }, [betOrRaiseInfo]);

    if (gameStatus === 'HAND_COMPLETE' || gameStatus === 'WAITING') {
        return (
            <Paper elevation={3} sx={{ p: 2, bgcolor: 'rgba(0,0,0,0.5)', color: 'white' }}>
                <Typography variant="h6" align="center">Hand Over</Typography>
                <Button variant="contained" color="primary" onClick={onNextHand} disabled={loading} fullWidth sx={{mt: 2}}>
                    {loading ? 'Starting...' : 'Next Hand'}
                </Button>
            </Paper>
        );
    }
    if (!validActions || validActions.length === 0) {
        return <Typography>Waiting for other players...</Typography>;
    }

    const canCheck = validActions.some(a => a.type === 'CHECK');
    const canCall = validActions.some(a => a.type === 'CALL');
    const canFold = validActions.some(a => a.type === 'FOLD');
    const callAmount = validActions.find(a => a.type === 'CALL')?.amount || 0;

    return (
        <Paper elevation={3} sx={{ p: 2, bgcolor: 'rgba(0,0,0,0.5)', color: 'white' }}>
            <Typography variant="h6" align="center" gutterBottom>Your Action</Typography>
            <Box sx={{ display: 'flex', justifyContent: 'space-around', alignItems: 'center', mb: 2 }}>
                {canFold && <Button variant="contained" color="error" onClick={() => onAction({ type: 'FOLD' })} disabled={loading}>Fold</Button>}
                {canCheck && <Button variant="contained" color="warning" onClick={() => onAction({ type: 'CHECK' })} disabled={loading}>Check</Button>}
                {canCall && <Button variant="contained" color="success" onClick={() => onAction({ type: 'CALL', amount: callAmount })} disabled={loading}>Call ${callAmount}</Button>}
            </Box>
            {betOrRaiseInfo && (
                <Box sx={{ mt: 2 }}>
                    <Typography gutterBottom>{betOrRaiseInfo.type}: ${raiseAmount}</Typography>
                    <Slider value={raiseAmount} min={betOrRaiseInfo.min} max={betOrRaiseInfo.max} step={10} onChange={(_, newValue) => setRaiseAmount(newValue)} valueLabelDisplay="auto" />
                    <Button variant="contained" color="primary" onClick={() => onAction({ type: betOrRaiseInfo.type, amount: raiseAmount })} disabled={loading || raiseAmount < betOrRaiseInfo.min || raiseAmount > betOrRaiseInfo.max} fullWidth>
                        {betOrRaiseInfo.type} to ${raiseAmount}
                    </Button>
                </Box>
            )}
        </Paper>
    );
};

export default PlayerActions;

