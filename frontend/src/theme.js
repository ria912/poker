// src/theme.js
import { createTheme } from '@mui/material';

export const darkTheme = createTheme({
    palette: {
        mode: 'dark',
        background: { default: '#121212', paper: '#1e1e1e' },
        primary: { main: '#f0a500' },
        secondary: { main: '#4caf50' },
    },
    typography: { fontFamily: 'Roboto, sans-serif' },
});