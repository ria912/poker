// src/components/GameTable.jsx
import React from 'react';
import { Box, Typography } from '@mui/material';
import Seat from './Seat';
import PokerCard from './PokerCard';

const GameTable = ({ seats, communityCards, pot, currentSeatIndex }) => {
    
    // --- ここからが新しいロジック ---
    const numSeats = 6; // 表示する座席の総数
    const seatPositions = [];

    const hCenter = 50; // テーブルの水平中心 (%)
    const vCenter = 50; // テーブルの垂直中心 (%)
    const hRadius = 40; // 水平方向の半径 (%) - テーブルを楕円にする
    const vRadius = 32; // 垂直方向の半径 (%)

    for (let i = 0; i < numSeats; i++) {
        // 時計回りに席を配置するための角度を計算します。
        // 角度90度（真下）をスタート地点とします。
        const angle = 90 + (360 / numSeats) * i;
        const angleRad = (angle * Math.PI) / 180; // ラジアンに変換

        const left = hCenter + hRadius * Math.cos(angleRad);
        const top = vCenter + vRadius * Math.sin(angleRad);

        seatPositions.push({
            // 計算した座標が要素の中心になるように調整
            transform: 'translate(-50%, -50%)', 
            position: 'absolute',
            left: `${left}%`,
            top: `${top}%`,
        });
    }
    // --- ここまで ---

    return (
        <Box sx={{
            position: 'relative',
            width: '100%',
            height: '500px',
            border: '10px solid #8B4513',
            borderRadius: '150px',
            boxSizing: 'border-box'
        }}>
            {/* Seats */}
            {seats.map(seat => (
                <Seat
                    key={seat.index}
                    seat={seat}
                    isCurrentPlayer={seat.index === currentSeatIndex}
                    // 動的に計算したスタイルを適用
                    style={seatPositions[seat.index]}
                />
            ))}

            {/* Community Cards & Pot */}
            <Box sx={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                textAlign: 'center'
            }}>
                <Typography variant="h6" sx={{ color: 'white', fontWeight: 'bold' }}>
                    Pot: ${pot}
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                    {communityCards.map((card, index) => (
                        <PokerCard key={index} card={card} />
                    ))}
                </Box>
            </Box>
        </Box>
    );
};

export default GameTable;