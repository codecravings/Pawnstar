# 🤖 PawnStar: The Chess Analysis Tool That Makes Magnus Cry

> *"It's like having Stockfish as your therapist, but with more roasting and fewer existential crises."*

Welcome to **PawnStar** - the chess analysis platform that will either make you a chess master or thoroughly destroy your ego. Possibly both at the same time! 

## 🎯 What This Beast Does

PawnStar analyzes your chess games with the ruthless precision of a chess engine and the gentle encouragement of Gordon Ramsay critiquing burnt toast. Here's what you get:

### 🧠 **Brain-Melting Analysis Features**
- **Real Stockfish Analysis**: Not some wannabe engine - we're talking about the REAL DEAL™
- **Accuracy Calculations**: Find out exactly how much you disappointed the chess gods
- **Blunder Detection**: We'll point out your mistakes with surgical precision and zero mercy
- **Move Quality Assessment**: From "Brilliant!" to "What were you thinking?!"

### 🎨 **Eye-Candy Interface** 
- **Interactive Chess Board**: Click, drag, watch your hopes and dreams unfold
- **Tabbed Sidebar**: Because organizing chaos is important
- **Smooth Animations**: Your blunders never looked so beautiful
- **Dark Mode**: For those late-night "Why did I play that?!" sessions

### 📊 **Professional-Grade Features**

#### 🔍 **Opening Analysis**
- **ECO Code Classification**: Know your Sicilian from your Scandinavian
- **Opening Database**: 50+ openings with more personality than most humans
- **Performance Tracking**: See which openings make you cry the most

#### 🎯 **Multi-PV Analysis**
- **Top 3 Best Moves**: Because sometimes you need options (that you won't play anyway)
- **Engine Evaluations**: Precise centipawn scores for maximum self-torture
- **Alternative Lines**: "What if I wasn't terrible at chess?"

#### ⚔️ **Tactical Pattern Recognition**
- **🍴 Fork Detection**: "Your knight is attacking TWO pieces! How scandalous!"
- **📌 Pin Recognition**: "That piece can't move. Kind of like your rating."
- **🗡️ Skewer Analysis**: "Move the queen or lose the rook. Choose your pain."
- **🕳️ Trapped Pieces**: "Your bishop has nowhere to go. Just like your chess career."
- **⚔️ Double Attacks**: "Two pieces ganging up on one. Chess bullying at its finest."

#### 🏆 **Achievement System**
Earn badges for your chess journey:
- **🎯 Accuracy Master**: 90%+ accuracy (a.k.a. "Are you even human?")
- **💎 Perfectionist**: 95%+ accuracy (a.k.a. "Definitely not human")
- **🚫 Blunder Free**: Zero blunders in a game (a.k.a. "Photoshop?")
- **⚡ Brilliant Tactician**: 3+ brilliant moves (a.k.a. "The engine took over")
- **📊 Analysis Addict**: 10, 50, 100, 500, 1000 game milestones

#### 📈 **Performance Tracking**
- **Improvement Trends**: Watch your rating go up! (Or down. Usually down.)
- **Opening Mastery**: Which openings you're least terrible at
- **Color Performance**: Are you better as White or Black? (Spoiler: Neither)
- **Monthly Trends**: Seasonal depression in chess form

## 🚀 Getting Started (AKA "How to Install Disappointment")

### Prerequisites
- Node.js (because JavaScript runs the world, apparently)
- Python 3.8+ (for the backend magic)
- Stockfish Chess Engine (the actual brain of this operation)
- A healthy sense of humor about your chess skills

### Installation

1. **Clone this repository** (like you're cloning your future chess improvement):
```bash
git clone https://github.com/yourusername/pawnstar.git
cd pawnstar
```

2. **Backend Setup** (The Smart Stuff):
```bash
cd backend
pip install -r requirements.txt
```

3. **Add your Stockfish path** to `.env`:
```bash
STOCKFISH_PATH=C:\stockfish\stockfish.exe  # Windows
# or
STOCKFISH_PATH=/usr/local/bin/stockfish     # Linux/Mac
```

4. **Frontend Setup** (The Pretty Stuff):
```bash
cd frontend
npm install
```

### Running the Application

1. **Start the Backend** (The Brain):
```bash
cd backend
python main.py
```

2. **Start the Frontend** (The Face):
```bash
cd frontend
npm run dev
```

3. **Open your browser** to `http://localhost:3000` and prepare for emotional damage!

## 🎮 How to Use

1. **Enter a Chess.com or Lichess username**
2. **Click "Analyze"** and watch the magic happen
3. **Cry a little** when you see your accuracy percentage
4. **Learn from your mistakes** (or make new ones)
5. **Repeat until chess mastery** (estimated time: 47 years)

## 🌟 Features That'll Blow Your Mind

### 🎪 **Analysis Quality Descriptions**
- **✅ BEST!**: "Perfect engine move!" (Translation: You got lucky)
- **⚡ BRILLIANT!**: "Outstanding tactical play!" (Translation: Even a broken clock...)
- **👍 EXCELLENT!**: "Very strong play!" (Translation: Not terrible!)
- **😊 GOOD!**: "Solid move!" (Translation: Mediocre)
- **⚠️ INACCURACY!**: "Could be better!" (Translation: Oof)
- **🤦 MISTAKE!**: "Even your pieces are facepalming!" (Translation: Why?)
- **💀 BLUNDER!**: "Your opponent is doing a happy dance!" (Translation: RIP)

### 🎭 **Accuracy Ratings with Personality**
- **🏆 GODLIKE! (95%+)**: "Are you even human? 🤖"
- **💎 MASTERCLASS! (90%+)**: "Magnus is sweating! 😰"
- **⭐ EXCELLENT! (85%+)**: "Your chess engine approves! 👍"
- **✨ SOLID PLAY! (80%+)**: "Not bad, human! 🙂"
- **😐 DECENT EFFORT! (75%+)**: "Room for improvement! 📚"
- **😬 ROUGH GAME! (65%+)**: "Your pieces are questioning your choices! 🤔"
- **💀 MASSACRE! (<65%)**: "Even beginners are cringing! 🙈"

## 🔧 API Endpoints (For the Nerds)

### Game Analysis
- `POST /analyze` - Analyze recent games (prepare for therapy)
- `POST /analyze-game` - Analyze specific game URL

### Opening Wisdom
- `GET /openings/popular` - Most popular openings
- `GET /openings/suggestions/{username}` - Personalized suggestions

### Performance Tracking
- `GET /performance/{username}` - Your chess sins laid bare
- `GET /performance/{username}/trends` - Watch your soul leave your body over time
- `GET /performance/{username}/openings` - Which openings hurt you the most

## 🎯 Tech Stack (The Ingredients of Chaos)

### Frontend
- **React 18**: Because we like our components like we like our chess pieces - functional
- **Vite**: Fast builds for fast losses
- **Tailwind CSS**: Making things pretty while your rating isn't
- **Chess.js**: For all the chess logic we're too lazy to write

### Backend  
- **FastAPI**: Python web framework that's faster than your knight development
- **Stockfish**: The chess engine that makes us all look bad
- **SQLite**: Database that remembers all your mistakes
- **Python-Chess**: Chess library with more patience than your coach

## 🤝 Contributing (Join the Suffering)

Want to make this tool even more brutally honest? Here's how:

1. **Fork the repository** (like forking your opponent's king)
2. **Create a feature branch** (`git checkout -b feature/more-roasting`)
3. **Make your changes** (add more emotional damage)
4. **Test everything** (make sure the roasting is accurate)
5. **Create a Pull Request** (share your genius/madness)

### Contribution Ideas
- 🎨 **More roasting messages** (we can always be more creative with insults)
- 🏆 **New achievements** ("Opened with 1.h4 and survived")
- 📊 **Better visualizations** (graphs that show your descent into madness)
- 🤖 **AI opponent** (for when you want to lose faster)
- 🎵 **Sound effects** (sad trombone for blunders)

## ⚠️ Disclaimer

This application may cause:
- Sudden realization of chess incompetence
- Excessive study of opening theory at 3 AM
- Compulsive analysis of every game ever played
- Questioning of life choices
- Addiction to tactical puzzles
- Spontaneous chess notation in casual conversation

**Use responsibly.** Side effects may include chess improvement.

## 📜 License

MIT License - Because sharing chess pain should be free for everyone.

## 🙏 Acknowledgments

- **Stockfish developers** - For creating the engine that humbles us all
- **Chess.com & Lichess** - For providing the data that exposes our weaknesses
- **Every chess player** - Who has ever wondered "Why did I play that?!"
- **Coffee** - The real MVP of late-night debugging sessions

---

*"In chess, as in life, the pawns go first. But in PawnStar, the pawns judge you."* ♟️

**Remember**: Every chess master was once a beginner who refused to give up. But also, every chess master probably didn't have access to analysis this brutally honest. You're welcome! 😈

🎯 **Ready to discover how bad you really are at chess?** Let's go! 🚀
