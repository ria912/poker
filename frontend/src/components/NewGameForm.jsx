// src/components/NewGameForm.jsx
import React, { useState } from 'react';
import { Box, Button, TextField, Typography, Paper } from '@mui/material';

const NewGameForm = ({ onNewGame, loading }) => {
    const [playerName, setPlayerName] = useState('Hero');
    const handleSubmit = (e) => {
        e.preventDefault();
        onNewGame([
            { name: playerName, stack: 1000, is_ai: false }, { name: 'Alice', stack: 1000, is_ai: true },
            { name: 'Bob', stack: 1000, is_ai: true }, { name: 'Charlie', stack: 1000, is_ai: true },
            { name: 'Dave', stack: 1000, is_ai: true }, { name: 'Eve', stack: 1000, is_ai: true },
        ]);
    };

    return (
        <Paper elevation={3} sx={{ p: 3, mt: 4, bgcolor: 'rgba(255,255,255,0.1)' }}>
            <Typography variant="h5" align="center" gutterBottom>Start a New Game</Typography>
            <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <TextField label="Your Name" variant="outlined" value={playerName} onChange={(e) => setPlayerName(e.target.value)} InputLabelProps={{ style: { color: 'white' } }} sx={{ input: { color: 'white' } }} />
                <Button type="submit" variant="contained" size="large" disabled={loading}>{loading ? 'Starting...' : 'Deal In'}</Button>
            </Box>
        </Paper>
    );
};

export default NewGameForm;

