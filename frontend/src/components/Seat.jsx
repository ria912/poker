// src/components/Seat.jsx
import React from 'react';
import { Box, Typography, Chip, Stack } from '@mui/material';
import PokerCard from './PokerCard.jsx';

const Seat = ({ seat, isCurrentPlayer, isDealer, style, angle, gameStatus, currentRound }) => {
    if (!seat.is_occupied || !seat.player) return null;

    const angleRad = angle * (Math.PI / 180);
    const isShowdown = gameStatus === 'HAND_COMPLETE' || currentRound === 'SHOWDOWN';
    const isConcealedAi = seat.player.is_ai && !isShowdown;

    // Bet chip position
    const betRadius = 45;
    const betStyle = { position: 'absolute', top: '50%', left: '50%', transform: `translate(-50%, -50%) translate(${-betRadius * Math.cos(angleRad)}px, ${betRadius * Math.sin(angleRad)}px)`, zIndex: 2 };

    // --- Card positioning logic ---
    const cardsRadius = 75;
    let cardContainerRotation = 0;
    let cardContentRotation = 0;
    let cardTranslation;

    if (isShowdown) {
        // In showdown, move cards below the player info box without rotation
        cardTranslation = `translateY(${cardsRadius}px)`;
    } else if (isConcealedAi) {
        // Concealed AI cards are closer and not rotated
        cardTranslation = `translate(${45 * Math.cos(angleRad)}px, ${-45 * Math.sin(angleRad)}px)`;
    } else {
        // Revealed human/AI cards are positioned along the circle edge
        cardTranslation = `translate(${cardsRadius * Math.cos(angleRad)}px, ${-cardsRadius * Math.sin(angleRad)}px)`;
        cardContainerRotation = angle - 90;
        cardContentRotation = 90 - angle;
    }
    
    const cardsStyle = { 
        position: 'absolute', 
        top: '50%', 
        left: '50%', 
        transform: `translate(-50%, -50%) ${cardTranslation} rotate(${cardContainerRotation}deg)`, 
        zIndex: 3 
    };

    const cardHeight = isConcealedAi ? 30 : 60;
    const cardSpacing = isConcealedAi ? -2 : 1;

    const renderCards = () => {
        const shouldShowCards = seat.hole_cards.length > 0 && (!seat.player.is_ai || (isShowdown && seat.status !== 'FOLDED'));
        if (shouldShowCards) {
            return seat.hole_cards.map((card, index) => <PokerCard key={`player-card-${seat.index}-${index}`} card={card} height={cardHeight} rotationAngle={cardContentRotation} />);
        }
        if (isConcealedAi && (seat.status === 'ACTIVE' || seat.status === 'ALL_IN')) {
            return <> <PokerCard isHidden={true} height={cardHeight} rotationAngle={cardContentRotation} /> <PokerCard isHidden={true} height={cardHeight} rotationAngle={cardContentRotation} /> </>;
        }
        return null;
    };

    return (
        <Box sx={{ ...style, width: 100, height: 100 }}>
            {seat.current_bet > 0 && <Box sx={betStyle}><Chip label={`${seat.current_bet}`} size="small" sx={{ color: 'white', fontWeight: 'bold', bgcolor: 'rgba(0,0,0,0.7)', border: '1px solid', borderColor: 'primary.main' }} /></Box>}
            <Box sx={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', p: '4px 12px', bgcolor: 'rgba(40, 40, 40, 0.8)', borderRadius: 2, textAlign: 'center', border: isCurrentPlayer ? '2px solid' : '1px solid', borderColor: isCurrentPlayer ? 'primary.main' : 'grey.700', boxShadow: isCurrentPlayer ? `0 0 12px #f0a500` : 'none', minWidth: '90px', zIndex: 1 }}>
                <Typography variant="body2" sx={{ fontWeight: 'bold', color: 'grey.400', whiteSpace: 'nowrap' }}>{seat.position}</Typography>
                <Typography variant="h6" sx={{ color: 'white' }}>{seat.stack}</Typography>
                {isDealer && <Chip label="D" size="small" sx={{ bgcolor: 'white', color: 'black', fontWeight: 'bold', position: 'absolute', top: -10, right: -10 }} />}
                {seat.status !== 'ACTIVE' && seat.status !== 'ALL_IN' && <Typography variant="caption" sx={{ color: 'error.main', position: 'absolute', top: '100%', left: '50%', transform: 'translateX(-50%)', whiteSpace: 'nowrap' }}>{seat.status}</Typography>}
            </Box>
            <Box sx={cardsStyle}><Stack direction={"row"} spacing={cardSpacing}>{renderCards()}</Stack></Box>
        </Box>
    );
};

export default Seat;

