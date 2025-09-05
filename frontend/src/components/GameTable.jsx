import React from 'react';
import { Box, Typography, Stack } from '@mui/material';
import Seat from './Seat';
import PokerCard from './PokerCard';

const GameTable = ({ seats, communityCards, pot, currentSeatIndex, dealerSeatIndex }) => {

    const occupiedSeats = seats.filter(s => s.is_occupied).sort((a, b) => a.index - b.index);
    const numPlayers = occupiedSeats.length;
    if (numPlayers === 0) return null; // プレイヤーがいない場合は何も表示しない

    const humanPlayerSeat = seats.find(s => s.player && !s.player.is_ai);
    // 人間プレイヤーを基準（下方向）にするための角度オフセットを計算
    const angleOffset = humanPlayerSeat ? -humanPlayerSeat.index * (360 / numPlayers) : 0;
    
    return (
        <Box sx={{
            position: 'relative',
            width: '100%',
            height: '100%',
        }}>
            
            {/* Player Seats */}
            {occupiedSeats.map((seat, i) => {
                 // 各プレイヤーを円形に配置するための角度を計算
                const angleDeg = (270 + angleOffset + i * (360 / numPlayers)) % 360;
                const angleRad = angleDeg * (Math.PI / 180);

                // 円周上の位置を計算 (中心50%, 半径は親要素に対する%)
                const hRadius = 40;
                const vRadius = 40;
                const top = 50 - vRadius * Math.sin(angleRad);
                const left = 50 + hRadius * Math.cos(angleRad);

                const style = {
                    position: 'absolute',
                    top: `${top}%`,
                    left: `${left}%`,
                    transform: 'translate(-50%, -50%)',
                };
                
                return (
                     <Seat
                        key={`seat-${seat.index}`}
                        seat={seat}
                        isCurrentPlayer={seat.index === currentSeatIndex}
                        isDealer={seat.index === dealerSeatIndex}
                        style={style}
                        angle={angleDeg} // Seatコンポーネントに角度を渡す
                    />
                )
            })}

            {/* Community Cards & Pot */}
            <Box sx={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                textAlign: 'center',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: 1.5,
                zIndex: 1,
            }}>
                <Typography variant="h5" sx={{ color: 'white', fontWeight: 'bold', bgcolor: 'rgba(0,0,0,0.5)', px: 2, py: 0.5, borderRadius: 2 }}>
                    Pot: {pot}
                </Typography>
                <Stack direction="row" spacing={1} justifyContent="center">
                    {communityCards.map((card, index) => (
                        <PokerCard key={`community-card-${index}`} card={card} height={60} />
                    ))}
                </Stack>
            </Box>
        </Box>
    );
};

export default GameTable;

