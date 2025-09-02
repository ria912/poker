// src/components/Seat.jsx
import React from 'react';
import { Box, Typography, Paper, Chip } from '@mui/material';
import PokerCard from './PokerCard';

const Seat = ({ seat, isCurrentPlayer, style }) => {
    if (!seat.is_occupied || !seat.player) {
        return null; // 空席は表示しない
    }

    const player = seat.player;

    return (
        <Paper
            elevation={isCurrentPlayer ? 12 : 3}
            sx={{
                position: 'absolute',
                ...style,
                p: 1.5,
                bgcolor: isCurrentPlayer ? 'rgba(255, 255, 0, 0.3)' : 'rgba(0, 0, 0, 0.5)',
                color: 'white',
                borderRadius: '8px',
                border: isCurrentPlayer ? '2px solid yellow' : '2px solid gray',
                minWidth: '140px', // 少し幅を広げる
                textAlign: 'center',
                transition: 'all 0.3s ease',
            }}
        >
            <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 1 }}>
                <Typography variant="subtitle1" sx={{ fontWeight: 'bold' }}>
                    {player.name}
                </Typography>
                {/* --- ポジション表示を追加 --- */}
                {seat.position && (
                    <Chip label={seat.position} color="secondary" size="small" sx={{ height: '18px' }} />
                )}
            </Box>
            
            <Typography variant="h6" sx={{ color: '#4caf50', fontWeight: 'bold' }}>
                ${seat.stack}
            </Typography>
            
            {/* Hole Cards */}
            <Box sx={{ display: 'flex', justifyContent: 'center', gap: 0.5, my: 1 }}>
                {seat.hole_cards.length > 0 ? (
                    seat.hole_cards.map((card, index) => <PokerCard key={index} card={card} height={60} />)
                ) : (
                    // AIの裏向きカード
                    <>
                        <PokerCard isHidden={true} height={60} />
                        <PokerCard isHidden={true} height={60} />
                    </>
                )}
            </Box>

            {seat.current_bet > 0 && (
                <Chip label={`Bet: $${seat.current_bet}`} color="primary" size="small" />
            )}
             {seat.status !== 'ACTIVE' && (
                <Chip label={seat.status} color="error" size="small" sx={{mt: 0.5}} />
            )}
        </Paper>
    );
};

export default Seat;