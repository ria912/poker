// src/components/GameTable.jsx
import React from 'react';
import { Box, Typography, Stack } from '@mui/material';
import Seat from './Seat.jsx';
import PokerCard from './PokerCard.jsx';

const GameTable = ({ seats, communityCards, pot, currentSeatIndex, dealerSeatIndex, gameStatus, currentRound }) => {
    const occupiedSeats = seats;
    const numPlayers = occupiedSeats.length;
    if (numPlayers === 0) return null;

    const humanPlayerSeat = occupiedSeats.find(s => s.player && !s.player.is_ai);
    const humanPlayerDisplayIndex = humanPlayerSeat 
        ? occupiedSeats.findIndex(s => s.index === humanPlayerSeat.index) 
        : -1;

    return (
        <Box sx={{ position: 'relative', width: '100%', height: '100%' }}>
            {occupiedSeats.map((seat, i) => {
                const step = 360 / numPlayers;
                const baseAngle = humanPlayerDisplayIndex !== -1 
                    ? (270 + humanPlayerDisplayIndex * step) 
                    : 270;
                
                const angleDeg = (baseAngle - i * step + 360) % 360;

                const angleRad = angleDeg * (Math.PI / 180);
                const hRadius = 40, vRadius = 40;
                const top = 50 - vRadius * Math.sin(angleRad);
                const left = 50 + hRadius * Math.cos(angleRad);
                const style = { position: 'absolute', top: `${top}%`, left: `${left}%`, transform: 'translate(-50%, -50%)' };

                return <Seat key={`seat-${seat.index}`} seat={seat} isCurrentPlayer={seat.index === currentSeatIndex} isDealer={seat.index === dealerSeatIndex} style={style} angle={angleDeg} gameStatus={gameStatus} currentRound={currentRound} />
            })}

            <Box sx={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 1.5, zIndex: 1 }}>
                <Typography variant="h5" sx={{ color: 'white', fontWeight: 'bold', bgcolor: 'rgba(0,0,0,0.5)', px: 2, py: 0.5, borderRadius: 2 }}>Pot: {pot}</Typography>
                <Stack direction="row" spacing={1} justifyContent="center">{communityCards.map((card, index) => <PokerCard key={`community-card-${index}`} card={card} height={60} />)}</Stack>
            </Box>
        </Box>
    );
};

export default GameTable;

