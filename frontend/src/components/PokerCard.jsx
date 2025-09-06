// src/components/PokerCard.jsx
import React from 'react';
import { Box, Typography } from '@mui/material';

const PokerCard = ({ card, height = 70, isHidden = false, rotationAngle = 0 }) => {
    const isSmall = height < 30;

    if (isHidden) {
        return (
            <Box
                sx={{
                    width: height * 0.7,
                    height: height,
                    borderRadius: 1,
                    background: 'linear-gradient(135deg, #333, #666)',
                    border: '1px solid #888'
                }}
            />
        );
    }
    
    if (!card || !card.suit) return null;

    const suitSymbols = { 'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣' };
    const suitColors = { 'H': '#ff4d4d', 'D': '#ff4d4d', 'S': '#ffffff', 'C': '#ffffff' };
    
    const upperCaseSuit = card.suit.toUpperCase();
    const suitSymbol = suitSymbols[upperCaseSuit];
    const suitColor = suitColors[upperCaseSuit] || 'white';
    const borderColor = (upperCaseSuit === 'H' || upperCaseSuit === 'D') ? '#ff4d4d' : '#555';

    return (
        <Box
            sx={{
                width: height * 0.7,
                height: height,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                bgcolor: '#2c2c2c',
                color: 'white',
                borderRadius: 1.5,
                border: `2px solid ${borderColor}`,
                boxShadow: '0 4px 8px rgba(0,0,0,0.3)',
                position: 'relative',
                userSelect: 'none',
                overflow: isSmall ? 'hidden' : 'visible',
            }}
        >
            <Box sx={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', transform: `rotate(${rotationAngle}deg)` }}>
                <Typography variant={isSmall ? 'caption' : 'h5'} sx={{ fontWeight: 'bold', lineHeight: 1 }}>
                    {card.rank}
                </Typography>
                 <Typography variant={isSmall ? 'caption' : 'h5'} sx={{ color: suitColor, lineHeight: 1 }}>
                    {suitSymbol}
                </Typography>
            </Box>
        </Box>
    );
};

export default PokerCard;

