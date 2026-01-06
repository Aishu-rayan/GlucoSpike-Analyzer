# Changelog

All notable changes to GlucoGuide will be documented in this file.

## [2.0.0] - 2025-12-30

### Major Features Added

#### 🔐 User Authentication & Accounts
- Secure user registration and login system
- bcrypt password hashing for security
- Cookie-based session management (7-day expiry)
- httpOnly secure cookies to prevent XSS
- Server-side session storage in SQLite

#### 💾 Persistent Chat History
- Save all conversations with food analyses
- Upload and store food images with chat messages
- Images stored on disk with paths in database
- Search through chat history
- Rename and delete chats
- Auto-generated chat titles from first message

#### 👤 User Profiles & Personalization
- Health status tracking:
  - Healthy (no conditions)
  - Insulin Resistance
  - Prediabetes
  - Type 1 Diabetes
  - Type 2 Diabetes
- Collect health metrics:
  - Age, sex, height, weight (BMI calculation)
  - Activity level (sedentary to very active)
  - Goals (weight loss, maintenance, health, diabetes management)
  - A1C levels, fasting glucose
  - Current medications
  - Other conditions
- 3-step onboarding wizard
- Profile settings page

#### 📈 Risk Score Engine
- Profile-adjusted insulin spike predictions
- Modifiers based on:
  - Insulin resistance status (+15-25%)
  - Diabetes type (+10-20%)
  - Diabetes duration (+5-15%)
  - BMI levels
  - Activity level (-15% to +10%)
  - A1C levels (+10-20% for elevated)
  - Medications (metformin, GLP-1: -10-15%)
  - Age factors (+5-10% for older adults)
- Different risk thresholds for diabetic vs non-diabetic users
- Personalized warnings and tips

#### 🔬 USDA FoodData Central Integration
- Access to comprehensive nutritional database
- Search functionality for USDA foods
- Automatic caching of results in SQLite
- Macronutrient data (carbs, protein, fat, fiber, calories)
- Serving size information
- Background refresh strategy

#### 📥 GI Data Import Pipeline
- CSV-based import system for GI values
- Track data sources (University of Sydney, Harvard, etc.)
- Confidence levels (high, medium, low)
- Source URLs for reference
- Notes field for additional information
- Export functionality for backup
- Sample CSV generator

#### 🎨 UI/UX Enhancements
- Left sidebar for chat history navigation
- Collapsible sidebar for focused view
- Beautiful login and registration pages
- Profile onboarding wizard with step progress
- User avatar and username display
- Search chats functionality
- Edit and delete chat actions
- Improved responsive design

### Backend Changes

#### New Modules
- `backend/db/`: SQLite database layer with SQLAlchemy
  - `engine.py`: Database engine and session management
  - `models.py`: 8 database models (User, Profile, Chat, Message, Attachment, Food, GIValue, Session)
  - `seed_data.py`: Initial data seeding script

- `backend/routes/`: API route handlers
  - `auth.py`: Authentication endpoints (register, login, logout, me)
  - `chats.py`: Chat CRUD and message management
  - `profile.py`: User profile management
  - `usda.py`: USDA API integration

- `backend/services/`: Business logic
  - `usda_service.py`: USDA API client with caching
  - Updated `egl_calculator.py`: Added ProfileContext, RiskScoreResult, profile modifiers

- `backend/scripts/`: Utility scripts
  - `import_gi_csv.py`: GI data import/export tool

#### Updated Files
- `main.py`: Added router mounting, database initialization
- `requirements.txt`: Added SQLAlchemy, aiosqlite, bcrypt, itsdangerous, starlette-session

### Frontend Changes

#### New Components & Pages
- `context/AuthContext.tsx`: Global authentication state management
- `pages/Login.tsx`: Login page with password visibility toggle
- `pages/Register.tsx`: Registration page with password requirements
- `pages/Onboarding.tsx`: 3-step profile setup wizard
- `components/Sidebar.tsx`: Chat history sidebar with search, edit, delete

#### Updated Files
- `App.tsx`: Added auth routing, multi-chat support, sidebar integration
- `api.ts`: Added auth, chat history, and profile API calls
- `types.ts`: Extended with auth, chat, profile types

### Database Additions
- 8 new tables with proper relationships and indexes
- Foreign key constraints with cascade deletes
- Timestamps on all entities
- JSON fields for flexible data storage
- Unique constraints on usernames and user profiles

### Security Improvements
- Password complexity validation
- SQL injection prevention (SQLAlchemy ORM)
- Session token security
- File path validation for uploads
- User isolation (can only access own data)

## [1.0.0] - 2025-12-26

### Initial Release

#### Core Features
- Food image recognition with GPT-4 Vision
- Glycemic Index database (80+ foods)
- Effective Glycemic Load calculation
- Macronutrient modifier system (fiber, protein, fat)
- Real-time chat interface
- Beautiful dark theme UI
- Recommendations for reducing insulin spikes

#### Technologies
- Backend: FastAPI, Python, OpenAI API
- Frontend: React, TypeScript, Tailwind CSS, Framer Motion
- In-memory food database

---

## Migration Notes

### v1.0 to v2.0

#### Breaking Changes
- App now requires authentication (existing anonymous usage deprecated)
- `/api/chat` endpoint still works but doesn't save history
- Session cookies required for most endpoints

#### Data Migration
- No migration needed - fresh installs create database automatically
- Existing users: Database will be created on first v2.0 startup

#### New Dependencies
- Backend: sqlalchemy, aiosqlite, bcrypt, itsdangerous, starlette-session
- Frontend: No new dependencies (uses existing React ecosystem)




