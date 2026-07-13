# ✈️ AI Smart Travel Planner

**Personalized AI-powered travel planning — Generate seamless itineraries, transit guides, local safety briefs, and accommodation advice all in one place.**

---

## 🗺️ Problem & Solution

Traditional travel planning apps rely on static templates and generic routes that ignore what truly matters:

- Individual origins and varied home departure transits
- Real-time regional variables, documentation, and weather realities
- Strict budget tiers and destination-specific hidden costs
- Personal interests, hobbies, and traveler configurations

This AI-powered travel agent uses **Google Gemini 2.5 Flash API** to tailor multi-variable schedules, destination strategies, and logistics plans to match each user's exact requirements — ensuring every journey is practical, personalized, and fully exportable.

---

## ✨ Features

| Feature | Description |
|:--------|:------------|
| 🗺️ **Itinerary Generator** | Day-by-day chronological schedule with Morning, Afternoon & Evening breakdown |
| 🏨 **Transport & Accommodation** | Neighborhood lodging choices and transit options filtered by budget tier |
| ☀️ **Weather & Local Advice** | Regional weather, cultural norms, safety checklist, currency & language basics |
| 📥 **Download Itinerary** | Export your full travel plan as a `.txt` file instantly |
| 🔁 **Auto Retry on Rate Limit** | Built-in 429 error backoff — auto-retries after 5 seconds |
| 💾 **Session Persistence** | Travel profile saved across tabs using `st.session_state` |

---

## 💻 Tech Stack

| Component | Technology |
|:----------|:-----------|
| **Frontend** | Streamlit |
| **AI Engine** | Google Gemini API (`models/gemini-2.5-flash`) |
| **Storage** | Session-State (`st.session_state`) + TXT Export |
| **Environment** | Python-dotenv (`.env` file) |
| **Language** | Python 3.12 |

---

## 📁 Project Structure

```
ai-smart-travel-planner/
│
├── app.py              → Main Streamlit application
├── requirements.txt    → Project dependencies
└── README.md           → Project documentation
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.12
- pip package manager
- Google Gemini API Key (free from Google AI Studio)

---

### Step-by-Step

#### ✅ Step 1 — Clone the Repository

```bash
git clone https://github.com/mrayanghosh/ai-smart-travel-planner
cd ai-smart-travel-planner
```

#### ✅ Step 2 — Install Dependencies

```bash
pip install -r requirements.txt
```

#### ✅ Step 3 — Get Your Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click **Get API Key** → Create new key
4. Copy the key

#### ✅ Step 4 — Create `.env` File

Create a file named `.env` in the project root:

```env
YOUR_GOOGLE_API_KEY=your_actual_gemini_api_key_here
```

> ⚠️ **Important:** Never push your `.env` file to GitHub! Add it to `.gitignore`:
> ```
> .env
> ```

#### ✅ Step 5 — Run the App

```bash
streamlit run app.py
```

The app will open automatically at `http://localhost:8501`

---

## 🕹️ How to Use

```
1. Fill in your Trip Preferences in the sidebar
   → Starting point, Destination, Duration, Budget, Travelers, Interests

2. Click "Save Trip Parameters"

3. Tab 1 — 🗺️ Smart Itinerary Builder
   → Add any custom requests
   → Click "Generate Complete Smart Itinerary"
   → Download the plan as .txt

4. Tab 2 — 🏨 Transport & Accommodation
   → Click "Analyze Transport & Accommodation Options"
   → Get neighborhood & transit recommendations

5. Tab 3 — ☀️ Weather & Local Advice
   → Click "Fetch Local Context Guides"
   → Get weather, safety, currency & language tips
```

---

## 🔧 Troubleshooting

| Issue | Solution |
|:------|:---------|
| **API Error 429** | Rate limit hit — app auto-retries after 5 seconds |
| **API Error 404** | Version mismatch — already fixed via `api_version: v1` |
| **ImportError on launch** | Run `pip install --upgrade google-genai streamlit python-dotenv pillow` |
| **Blank output** | Check your `.env` file — make sure API key is correct |

---

## 👨‍💻 Author

**Ayan Ghosh**

🔗 GitHub: [github.com/mrayanghosh](https://github.com/mrayanghosh)

---

## 📄 License

This project is open source and free to use for learning and personal projects.
