// src/components/GameLog.jsx
import React from 'react';
import { Paper, Typography } from '@mui/material';

const GameLog = ({ message }) => {
    // メッセージ内の半角スペースを改行に変換する
    const formattedMessage = (message || 'Welcome to the game!')
        .split(' ')
        .map((text, index) => (
            <React.Fragment key={index}>
                {text}
                <br />
            </React.Fragment>
        ));

    return (
        <Paper
            elevation={3}
            sx={{
                p: 2,
                bgcolor: 'rgba(0, 0, 0, 0.5)',
                color: 'white',
                height: '100%',
                overflowY: 'auto',
            }}
        >
            <Typography variant="h6" gutterBottom>Game Log</Typography>
            <Typography variant="body1" component="div">
                {formattedMessage}
            </Typography>
        </Paper>
    );
};

export default GameLog;