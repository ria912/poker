import React, { useRef } from 'react';
import { Box, Chip, Stack, IconButton } from '@mui/material';

// SVG Icons for arrows to avoid extra dependencies
const ArrowLeftIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
        <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z" />
    </svg>
);

const ArrowRightIcon = () => (
     <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
        <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z" />
    </svg>
);

const GameLog = ({ message }) => {
    const scrollRef = useRef(null);

    // Backendからのメッセージを '.' で分割してアクションの配列を作成
    const actions = message ? message.trim().split('.').filter(Boolean) : ['New hand started'];

    // スクロールボタンがクリックされたときの処理
    const handleScroll = (direction) => {
        if (scrollRef.current) {
            const scrollAmount = 300; // 1回のクリックでのスクロール量
            const currentScroll = scrollRef.current.scrollLeft;
            const newScroll = direction === 'left' ? currentScroll - scrollAmount : currentScroll + scrollAmount;
            
            // スムーズスクロールで移動
            scrollRef.current.scrollTo({
                left: newScroll,
                behavior: 'smooth',
            });
        }
    };

    return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <IconButton onClick={() => handleScroll('left')} size="small" sx={{ bgcolor: 'rgba(255,255,255,0.1)' }}>
                <ArrowLeftIcon />
            </IconButton>

            <Box
                ref={scrollRef}
                sx={{
                    flexGrow: 1,
                    overflow: 'hidden', // スクロールバーは非表示にする
                    whiteSpace: 'nowrap',
                }}
            >
                <Stack direction="row" spacing={1} sx={{ p: '2px' }}>
                    {actions.map((text, index) => (
                       <Chip
                            key={index}
                            label={text.trim()}
                            variant="outlined"
                            size="small"
                            sx={{ color: '#ccc', borderColor: '#555' }}
                        />
                    ))}
                </Stack>
            </Box>

            <IconButton onClick={() => handleScroll('right')} size="small" sx={{ bgcolor: 'rgba(255,255,255,0.1)' }}>
                <ArrowRightIcon />
            </IconButton>
        </Box>
    );
};

export default GameLog;
