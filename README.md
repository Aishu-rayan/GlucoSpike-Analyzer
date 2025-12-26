# 🥗 GlucoGuide - Insulin Spike Management Chatbot

An AI-powered chatbot that analyzes food images and calculates the Effective Glycemic Load (eGL) to help health-conscious users understand their food's impact on insulin levels.

![GlucoGuide](https://img.shields.io/badge/GlucoGuide-v1.0.0-green)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![React](https://img.shields.io/badge/React-18-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)

## ✨ Features

- **🖼️ Food Image Recognition**: Upload food photos for AI-powered identification
- **📊 Glycemic Analysis**: Calculate Base GL and Effective GL (eGL)
- **🧮 Macronutrient Modifiers**: Protein, fat, and fiber impact calculations
- **💡 Smart Recommendations**: Personalized tips to reduce insulin spikes
- **💬 Chat Interface**: Natural conversation about nutrition

## 🎯 How It Works

### Effective Glycemic Load (eGL) Calculation

1. **Base GL** = (GI × Net Carbs) / 100
2. **Macronutrient Modifiers Applied**:
   - Fiber: Up to 20% reduction
   - Protein: Up to 20% reduction  
   - Fat: Up to 15% reduction
3. **eGL** = Base GL × (1 - modifiers)

### Spike Classification

| eGL Range | Level | Guidance |
|-----------|-------|----------|
| 0-10 | LOW | ✅ Safe to eat freely |
| 11-19 | MODERATE | ⚠️ Eat in moderation |
| 20+ | HIGH | ❌ Limit or mitigate |

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- OpenAI API Key

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo OPENAI_API_KEY=your_api_key_here > .env

# Run the server
python main.py
```

The API will be available at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The app will be available at `http://localhost:5173`

## 📁 Project Structure

```
insulin_spike_management/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   ├── database/
│   │   ├── __init__.py
│   │   └── gi_database.py      # GI & nutrition database
│   ├── services/
│   │   ├── __init__.py
│   │   ├── egl_calculator.py   # eGL calculation logic
│   │   └── food_analyzer.py    # OpenAI Vision integration
│   └── models/
│       ├── __init__.py
│       └── schemas.py          # Pydantic models
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── index.html
│   └── src/
│       ├── App.tsx             # Main React component
│       ├── main.tsx            # Entry point
│       ├── index.css           # Global styles
│       ├── types.ts            # TypeScript types
│       ├── api.ts              # API client
│       └── components/
│           ├── Header.tsx
│           ├── ChatMessage.tsx
│           ├── ChatInput.tsx
│           ├── EGLResultCard.tsx
│           ├── WelcomeScreen.tsx
│           └── LoadingMessage.tsx
│
├── initial_plan.txt            # Project planning document
└── README.md
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Detailed health status |
| POST | `/api/analyze/image` | Analyze food image |
| POST | `/api/analyze/food` | Analyze food by name |
| GET | `/api/foods/search` | Search food database |
| GET | `/api/foods` | List all foods |
| GET | `/api/foods/categories` | List food categories |
| POST | `/api/chat` | General chat |

## 🍎 Sample Foods in Database

- **Grains**: Rice (white, brown, basmati), pasta, bread, oatmeal, quinoa
- **Fruits**: Apple, banana, orange, mango, berries
- **Vegetables**: Potato, sweet potato, broccoli, carrots, spinach
- **Proteins**: Chicken, salmon, eggs, tofu, beef
- **Legumes**: Lentils, chickpeas, beans
- **Indian Foods**: Chapati, roti, naan, dosa, idli, dal, biryani
- **And 80+ more foods...**

## 💡 Tips for Best Results

1. **Take clear photos** with good lighting
2. **Include the whole plate** for accurate portion estimation
3. **Ask follow-up questions** about specific foods
4. **Combine high-GL foods** with protein and fiber

## 🔐 Environment Variables

Create a `.env` file in the backend directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## 📝 License

MIT License - feel free to use and modify!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

**Note**: This application is for educational purposes only and should not be considered medical advice. Always consult with a healthcare professional for personalized nutrition guidance.

