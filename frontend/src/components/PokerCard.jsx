import React from 'react';
import { Box, Typography } from '@mui/material';

// ★★★ 変更点1: rotationAngle prop を追加 ★★★
const PokerCard = ({ card, height = 70, isHidden = false, rotationAngle = 0 }) => {
    
    if (isHidden) {
        return (
            <Box
                sx={{
                    width: height * 0.7,
                    height: height,
                    borderRadius: 1.5,
                    background: 'linear-gradient(135deg, #333, #666)',
                    border: '2px solid #888'
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
            }}
        >
            {/* ★★★ 変更点2: 中身をBoxで囲み、逆回転を適用 ★★★ */}
            <Box sx={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                transform: `rotate(${rotationAngle}deg)`
            }}>
                <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                    {card.rank}
                </Typography>
                 <Typography variant="h5" sx={{ color: suitColor, lineHeight: 1 }}>
                    {suitSymbol}
                </Typography>
            </Box>
        </Box>
    );
};

export default PokerCard;
