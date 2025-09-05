import React from 'react';
import { Box, Typography, Chip, Stack } from '@mui/material';
import PokerCard from './PokerCard.jsx';

const Seat = ({ seat, isCurrentPlayer, isDealer, style, angle }) => {
    if (!seat.is_occupied || !seat.player) {
        return null;
    }

    const angleRad = angle * (Math.PI / 180);
    const betRadius = 45; 
    const cardsRadius = 75;

    const betStyle = {
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: `translate(-50%, -50%) translate(${-betRadius * Math.cos(angleRad)}px, ${betRadius * Math.sin(angleRad)}px)`,
        zIndex: 2,
    };
    
    const cardsStyle = {
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: `translate(-50%, -50%) translate(${cardsRadius * Math.cos(angleRad)}px, ${-cardsRadius * Math.sin(angleRad)}px) rotate(${angle - 90}deg)`,
        zIndex: 0,
    };

    const showHiddenCards = seat.player.is_ai && (seat.status === 'ACTIVE' || seat.status === 'ALL_IN');
    
    // カードの中身を逆回転させるための角度を計算
    const cardContentRotation = 90 - angle;

    return (
        <Box sx={{ ...style, width: 100, height: 100 }}>
            
            {seat.current_bet > 0 && (
                <Box sx={betStyle}>
                    <Chip 
                        label={`${seat.current_bet}`} 
                        color="primary" 
                        size="small" 
                        sx={{ bgcolor: 'rgba(0,0,0,0.7)', border: '1px solid', borderColor: 'primary.main' }} 
                    />
                </Box>
            )}

            <Box sx={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                p: '4px 12px',
                bgcolor: 'rgba(40, 40, 40, 0.8)',
                borderRadius: 2,
                textAlign: 'center',
                border: isCurrentPlayer ? '2px solid' : '1px solid',
                borderColor: isCurrentPlayer ? 'primary.main' : 'grey.700',
                boxShadow: isCurrentPlayer ? `0 0 12px #f0a500` : 'none',
                minWidth: '90px',
                zIndex: 1,
            }}>
                <Typography variant="body2" sx={{ fontWeight: 'bold', color: 'grey.400', whiteSpace: 'nowrap' }}>
                    {seat.position}
                </Typography>
                <Typography variant="h6" sx={{ color: 'white' }}>
                    {seat.stack}
                </Typography>
                
                 {isDealer && (
                    <Chip label="D" size="small" sx={{ 
                        bgcolor: 'white', color: 'black', fontWeight: 'bold', 
                        position: 'absolute', top: -10, right: -10,
                    }}/>
                )}

                {seat.status !== 'ACTIVE' && seat.status !== 'ALL_IN' && (
                     <Typography variant="caption" sx={{ color: 'error.main', position: 'absolute', top: '100%', left: '50%', transform: 'translateX(-50%)', whiteSpace: 'nowrap' }}>
                        {seat.status}
                    </Typography>
                )}
            </Box>

            <Box sx={cardsStyle}>
                {/* ★★★ 変更点1: カードの並び方を横に戻す ★★★ */}
                <Stack direction="row" spacing={1}>
                    {seat.hole_cards.length > 0 ? (
                        seat.hole_cards.map((card, index) => (
                            <PokerCard 
                                key={`player-card-${seat.index}-${index}`} 
                                card={card} 
                                height={60} 
                                // ★★★ 変更点2: 逆回転用の角度を渡す ★★★
                                rotationAngle={cardContentRotation} 
                            />
                        ))
                    ) : showHiddenCards ? (
                        <>
                            <PokerCard isHidden={true} height={60} rotationAngle={cardContentRotation} />
                            <PokerCard isHidden={true} height={60} rotationAngle={cardContentRotation} />
                        </>
                    ) : null}
                </Stack>
            </Box>
        </Box>
    );
};

export default Seat;

