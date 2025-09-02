// src/components/PokerCard.js
import React from 'react';
import { Paper } from '@mui/material';

const PokerCard = ({ card, height = 80, isHidden = false }) => {
    const suitSymbols = {
        'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣'
    };
    const suitColors = {
        'S': 'black', 'H': 'red', 'D': 'blue', 'C': 'green'
    };

    if (isHidden) {
        return (
            <Paper
                elevation={2}
                sx={{
                    width: height * 0.7,
                    height: height,
                    borderRadius: '5px',
                    background: 'linear-gradient(135deg, #444, #999)',
                    border: '1px solid #ccc'
                }}
            />
        );
    }
    
    if (!card) return null;

    return (
        <Paper
            elevation={3}
            sx={{
                width: height * 0.7,
                height: height,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                bgcolor: 'white',
                color: suitColors[card.suit] || 'black',
                borderRadius: '5px',
                fontSize: `${height * 0.3}px`,
                fontWeight: 'bold',
            }}
        >
            {card.rank}
            <span style={{ fontSize: `${height * 0.25}px` }}>{suitSymbols[card.suit]}</span>
        </Paper>
    );
};

export default PokerCard;