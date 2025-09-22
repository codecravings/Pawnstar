# Pawnstar Frontend

A React + Tailwind CSS frontend for chess game analysis with Stockfish engine integration.

## Features

- **Dark-first UI** with custom color palette
- **Mobile-responsive** layout
- **Real-time chess analysis** via FastAPI backend
- **Interactive board** with FEN position display
- **Evaluation graph** showing centipawn values over time
- **Move list** with blunder detection and highlighting
- **Meme overlay system** for blunder notifications
- **Micro-interactions** and animations

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

The app will open at `http://localhost:3000`.

## Backend Requirements

The frontend expects a FastAPI backend running at `http://127.0.0.1:8000` with the following endpoints:

- `GET /health` - Health check
- `POST /analyze/lichess` - Analyze Lichess games

Example request to analyze endpoint:
```json
{
  "username": "lichess_username",
  "max": 1,
  "depth": 12
}
```

## Meme Assets

For custom blunder memes, place image files in `/public/assets/memes/`. 

Supported formats: `.jpg`, `.png`, `.gif`, `.webp`

If no custom memes are found, the app will use built-in SVG placeholders.

## Color Palette

- Background: `#0B0F14`
- Surface: `#0F1720`
- Primary: `#7C5CFF`
- Accent: `#22D3EE`
- Danger: `#FF6B6B`
- Text: `#E6EEF3`

## Technologies

- React 18
- Tailwind CSS 3
- Vite (build tool)
- Axios (HTTP client)

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Topbar.jsx          # Username input and controls
│   │   ├── Board.jsx           # Chess board display
│   │   ├── EvalGraph.jsx       # Evaluation chart
│   │   ├── MoveList.jsx        # Move history with analysis
│   │   └── MemeOverlay.jsx     # Blunder notification overlay
│   ├── App.jsx                 # Main application layout
│   ├── index.js                # React entry point
│   └── index.css               # Global styles and Tailwind imports
├── package.json
├── tailwind.config.js
├── postcss.config.js
└── vite.config.js
```