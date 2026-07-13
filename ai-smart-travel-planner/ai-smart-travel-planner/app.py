import os
import time
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import streamlit as st

# Google Gemini SDK အား တင်သွင်းခြင်း
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Load environment variables safely from your local .env file
load_dotenv()

# Helper function to get a fresh client instance to prevent stale connection errors
def get_gemini_client(key_env_name):
    api_key = os.getenv(key_env_name)
    if not api_key:
        st.error(f"Missing environment variable: {key_env_name}")
        return None
    return genai.Client(api_key=api_key)

# --- Weather API Integration (Open-Meteo Daily Forecast) ---
def get_weather_forecast(location_name):
    """
    Fetches 7-day weather forecast using Open-Meteo by converting location names to coordinates.
    Returns day-by-day weather data starting from tomorrow.
    """
    try:
        # Step 1: Geocoding (Convert Location Name to Lat/Lon)
        geo_url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json&limit=1"
        headers = {'User-Agent': 'AISmartTravelPlanner/1.0'}
        geo_res = requests.get(geo_url, headers=headers, timeout=5).json()
        
        if not geo_res:
            return "Weather Data Unavailable (Location not found)", {}
        
        lat = geo_res[0]['lat']
        lon = geo_res[0]['lon']
        
        # Step 2: Fetch Daily Weather Forecast (including weather codes and max/min temperatures)
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=weathercode,temperature_2m_max,temperature_2m_min&timezone=auto"
        weather_res = requests.get(weather_url, timeout=5).json()
        
        daily_data = weather_res.get('daily', {})
        if not daily_data:
            return "Weather Forecast Data Unavailable", {}
            
        # WMO Weather interpretation codes
        def interpret_wmo_code(code):
            if code in [0, 1]: return "Clear/Sunny"
            elif code in [2, 3]: return "Partly Cloudy"
            elif code in [45, 48]: return "Foggy"
            elif code in [51, 53, 55, 61, 63, 65]: return "Light Rain / Rainy"
            elif code in [80, 81, 82, 95, 96, 99]: return "Heavy Rain / Stormy"
            else: return "Cloudy"

        # Build a structured text overview for the prompt and display
        forecast_str = ""
        forecast_dict = {}
        
        dates = daily_data.get('time', [])
        codes = daily_data.get('weathercode', [])
        max_temps = daily_data.get('temperature_2m_max', [])
        min_temps = daily_data.get('temperature_2m_min', [])
        
        for i in range(1, min(len(dates), 5)): # Get next few days starting from tomorrow
            date_obj = datetime.strptime(dates[i], "%Y-%m-%d")
            day_name = date_obj.strftime("%A")
            condition = interpret_wmo_code(codes[i])
            temp_range = f"{min_temps[i]}°C - {max_temps[i]}°C"
            
            day_label = f"Day {i}"
            forecast_dict[day_label] = f"{day_name} ({dates[i]}): {condition}, Temp: {temp_range}"
            forecast_str += f"- {day_label} ({day_name}, {dates[i]}): {condition} [{temp_range}]\n"
            
        return forecast_str, forecast_dict
    except Exception as e:
        return f"Weather Forecast Data Unavailable: {str(e)}", {}

# Initialize Session State variables for trip persistence
if 'travel_profile' not in st.session_state:
    st.session_state.travel_profile = {
        "Starting Point": "Yangon, Myanmar",
        "destination": "Bagan, Myanmar",
        "duration": 3,
        "budget": "Moderate / Mid-Range",
        "travelers": "2 Adults",
        "interests": "Pagodas, Culture, Local Food",
        "language": "မြန်မာဘာသာ (Burmese)"
    }

if 'generated_itinerary' not in st.session_state:
    st.session_state.generated_itinerary = None

# --- Tab-specific functions with fresh client instantiation and retry logic ---

def get_tab1_response(prompt):
    # Pass environment variable strings instead of active client objects
    keys = ["GEMINI_KEY_1", "GEMINI_KEY_2", "GEMINI_KEY_3"]
    last_error = None

    for key_name in keys:
        try:
            client = get_gemini_client(key_name)
            if not client:
                continue
                
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt],
                # Adding a config block ensures proper runtime options if needed
            )
            return response.text

        except Exception as e:
            last_error = str(e)
            # Switch key if server is busy, rate limited, or connection dropped
            if any(err in last_error.upper() for err in ["503", "UNAVAILABLE", "DISCONNECTED", "TIMEOUT"]):
                print(f"{key_name} failed/busy. Switching to next API key...")
                continue
            else:
                return f"{key_name} Error: {last_error}"

    return f"All Gemini API Keys failed to respond.\n\nLast Error: {last_error}"

def get_tab2_response(prompt):
    try:
        client = get_gemini_client("GEMINI_KEY_2")
        if not client: return "Error: GEMINI_KEY_2 missing."
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return f"Tab 2 (Gemini Key 2) Error: {str(e)}"

def get_tab3_response(prompt):
    try:
        client = get_gemini_client("GEMINI_KEY_3")
        if not client: return "Error: GEMINI_KEY_3 missing."
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        return f"Tab 3 (Gemini Key 3) Error: {str(e)}"

# --- App Layout Configuration ---
st.set_page_config(page_title="AI Smart Travel Planner", layout="wide")

# Custom UI styling injection
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
    div[data-testid="stExpander"] {
        border: 1px solid #E5E7EB;
        border-radius: 0.5rem;
        background-color: #F9FAFB;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">✈️ AI Smart Travel Planner Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">မြေပြင်အခြေအနေမှန်နှင့် ဒေသသုံးငွေကြေး အလိုအလျောက် တွက်ချက်စနစ် ပါဝင်သော AI ခရီးသွား လမ်းညွှန်စနစ်။</div>', unsafe_allow_html=True)

# Sidebar for Travel Preferences configuration
with st.sidebar:
    st.subheader("🎒 Trip Profile Setup")
    st.write("Configure your personalized parameters below:")
    st.markdown("---")
    
    origin = st.text_input("📍 Starting From", value=st.session_state.travel_profile["Starting Point"])
    dest = st.text_input("🏁 Destination", value=st.session_state.travel_profile["destination"])
    
    days = st.slider("📅 Duration (Days)", min_value=1, max_value=7, value=int(st.session_state.travel_profile["duration"]))
    budget = st.selectbox("💰 Budget Tier", ["Budget Friendly", "Moderate / Mid-Range", "Luxury / Premium"], index=1)
    party = st.text_input("👥 Travelers Group", value=st.session_state.travel_profile["travelers"])
    hobbies = st.text_area("🎯 Interests & Activities", value=st.session_state.travel_profile["interests"])
    
    selected_lang = st.selectbox(
        "🌐 Output Language", 
        ["မြန်မာဘာသာ (Burmese)", "English"], 
        index=0 if st.session_state.travel_profile["language"] == "မြန်မာဘာသာ (Burmese)" else 1
    )

    st.markdown("---")
    st.info("ℹ️ စနစ်လမ်းညွှန်ချက်: မြန်မာနိုင်ငံရှိ မြို့ငယ်/ရွာငယ်များ ရှာဖွေရာတွင် ပိုမိုတိကျစေရန် 'မြို့အမည်၊ တိုင်း/ပြည်နယ်၊ မြန်မာနိုင်ငံ' (ဥပမာ - ကလောမြို့၊ ရှမ်းပြည်နယ်) ဟု ရိုက်ထည့်ပေးပါ။")

    if st.button("✨ Save Travel Parameters", use_container_width=True, type="primary"):
        st.session_state.travel_profile = {
            "Starting Point": origin,
            "destination": dest,
            "duration": days,
            "budget": budget,
            "travelers": party,
            "interests": hobbies,
            "language": selected_lang
        }
        st.success("✅ Travel profile registered successfully!")

# Fetch live forecast data dynamically based on destination
weather_summary_text, weather_forecast_days = get_weather_forecast(st.session_state.travel_profile["destination"])

# Main Context Display Cards
with st.container():
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(label="Target Destination", value=st.session_state.travel_profile["destination"])
    with c2:
        st.metric(label="Length of Stay", value=f"{st.session_state.travel_profile['duration']} Days")
    with c3:
        tomorrow_weather = weather_forecast_days.get("Day 1", "Check Tab 3")
        st.metric(label="Tomorrow's Weather", value=tomorrow_weather.split(":")[1].split(",")[0] if ":" in tomorrow_weather else "Loaded") 
    with c4:
        st.metric(label="Output Language", value="Burmese" if "Burmese" in st.session_state.travel_profile["language"] else "English")

st.markdown("<br>", unsafe_allow_html=True)

# Main Tab Interfaces 
tab1, tab2, tab3 = st.tabs(["🗺 Smart Itinerary Builder", "🏨 Transport & Accommodation", "☀️ Weather & Local Advice"])

output_lang = "Burmese (မြန်မာဘာသာ)" if st.session_state.travel_profile["language"] == "မြန်မာဘာသာ (Burmese)" else "English"

with tab1:
    st.subheader("Tailored Day-by-Day Itinerary Planner")
    custom_requests = st.text_area("Any custom constraints? (Optional)", placeholder="e.g. traveling with seniors, wheelchair accessible, vegetarian options...", key="tab1_req")

    if st.button("🚀 Generate Complete Smart Itinerary", type="primary"):
        with st.spinner(f"AI က ခရီးစဉ်ကို {output_lang} ဖြင့် စဉ်းစားနေပါသည်..."):
            prompt = f"""
            You are an expert Local Smart Travel Planner Agent. Build a highly realistic, comprehensive, and engaging day-by-day travel itinerary based on this profile:
            Destination: {st.session_state.travel_profile['destination']}
            Duration: {st.session_state.travel_profile['duration']} Days (Starting from TOMORROW)
            Budget Tier: {st.session_state.travel_profile['budget']}
            Group Configuration: {st.session_state.travel_profile['travelers']}
            Core Interests: {st.session_state.travel_profile['interests']}
            Special User Constraints: {custom_requests if custom_requests else 'None provided'}
            
            CRITICAL DAY-BY-DAY WEATHER FORECAST RULES:
            The raw structured forecast timeline starting from tomorrow is:
            {weather_summary_text}
            
            You MUST break down the plan into exactly {st.session_state.travel_profile['duration']} distinct days. For each single day, read the corresponding weather condition from the data above and optimize:
            1. If a specific day is forecasted as 'Light Rain / Rainy' or 'Heavy Rain / Stormy': Design that specific day around indoor activities (e.g., covered historic pagodas/temples, local museums, indoor arts/crafts workshops, or culinary food tours). Explicitly skip risky outdoor boat trips, open-air trekking, or long e-bike routes on muddy tracks for that day.
            2. If a specific day is forecasted as 'Clear/Sunny' or 'Partly Cloudy': Prioritize outdoor exploration, sunset viewpoints, hiking, and boat rides for that specific day. Organize the timing to keep intense outdoor walking in the cool morning or late afternoon, escaping to shade during peak noon heat.
            CRITICAL REAL-TIME GROUND REALITY REQUIREMENTS (ESPECIALLY FOR MYANMAR):
            1. You must write the entire response in {output_lang} language.
            2. Write in a warm, welcoming, natural, and authentic local tour guide tone. Avoid mechanical, robotic translation.
            3. CRITICAL ON-GROUND FACT-CHECKING: Consider the actual current situation in 2026. If the selected destination or town has ongoing security constraints, night curfews, or road blockages, adjust the itinerary to strictly focus only on safe, verified zones and daytime travel.
            4. Provide specific names of active, local places to visit, recommended timing (Morning/Afternoon/Evening), and practical experiential tips. Keep it detailed and rich so the traveler can actually follow it.
            """
            st.session_state.generated_itinerary = get_tab1_response(prompt)

    if st.session_state.generated_itinerary:
        st.markdown("---")
        st.info("💡 Your Generated Plan:")
        st.markdown(st.session_state.generated_itinerary)
        
        if not st.session_state.generated_itinerary.startswith("All Gemini API Keys"):
            st.download_button(
                label="📥 Download Itinerary Text File",
                data=st.session_state.generated_itinerary,
                file_name=f"{st.session_state.travel_profile['destination'].replace(' ', '_')}_itinerary.txt",
                mime="text/plain",
                use_container_width=True
            )

with tab2:
    st.subheader("Recommended Logistics & Lodging Strategy")
    st.write("Get structural recommendations for transit routing and localized booking coordinates.")
    
    if st.button("🔍 Analyze Transport & Accommodation Options", type="primary"):
        with st.spinner(f"AI က တည်းခိုရန်နေရာနှင့် သွားလာရေးများကို {output_lang} ဖြင့် ရှာဖွေနေပါသည်..."):
            logistics_prompt = f"""
            You are an expert Local Logistics Advisory Agent. Provide a practical, safety-conscious, and highly detailed transport and lodging advisory for a trip to {st.session_state.travel_profile['destination']} in {output_lang} language.
            Budget Profile: {st.session_state.travel_profile['budget']} for {st.session_state.travel_profile['travelers']}.
            Live Weather Conditions: {weather_summary_text}

            CRITICAL REAL-TIME LOGISTICS & CURRENCY REQUIREMENTS (CURRENT YEAR 2026):
            1. RECENT GROUND TRUTH FACT-CHECK: You must provide logistics that match the actual current situation in Myanmar. Check if flights are genuinely operational to the specific destination. For towns/regions experiencing airport suspensions (like Loikaw or other conflict-impacted small towns), explicitly override old memory and state that flights are suspended, recommending ONLY specific, active Highway Express Buses or alternative land routes.
            2. TRANSPORT REALITIES: Account for longer travel durations, potential security checkpoints, and the necessity of daytime travel. Weather elements like rainy seasons blocking unpaved routes should be reflected based on the weather context provided.
            3. INFLATION-ADJUSTED LOCAL CURRENCY: You MUST display all estimated daily costs, bus/flight fares, and lodging rates in the official currency of the destination. For Myanmar, use Myanmar Kyat (MMK / ကျပ်) and make sure prices reflect realistic local market rates, accounting for recent commodity inflation.
            4. ACCOMMODATION: Suggest 2-3 specific localized safe-zone accommodation options (ranging from local guesthouses to hotels) matching the user's budget.
            5. Structure the advice beautifully using clear markdown headers and bullet points.
            """
            logistics_response = get_tab2_response(logistics_prompt)
            st.markdown("---")
            st.markdown(logistics_response)

with tab3:
    st.subheader("Live-Context Checks & Safety Advisory")
    st.write("Gain expert insights on local customs, packing guidelines, and seasonal realities.")
    
    if st.button("📋 Fetch Local Context Guides", type="primary"):
        with st.spinner(f"AI က ရာသီဥတုနှင့် ဒေသတွင်း အကြံပြုချက်များကို {output_lang} ဖြင့် ပြုစုနေပါသည်..."):
            insight_prompt = f"""
            You are an expert Local Insider and Safety Advisor. Provide an authentic, real-time safety and local context guide for {st.session_state.travel_profile['destination']} in {output_lang} language.
            
            LIVE WEATHER TIMELINE: 
            {weather_summary_text}

            CRITICAL REAL-TIME CONTEXT & SAFETY REQUIREMENTS:
            1. REAL-TIME SAFETY & ROAD CONDITIONS: Clearly state the current local situation. Highlight any necessary precautions like carrying physical ID cards/NRC, passing through security checkpoints, curfews, or local travel restrictions.
            2. LOCAL CONNECTIVITY: Mention which telecom network (e.g., Mytel, ATOM, MPT, Ooredoo) has the strongest data signal or coverage in this specific town/region.
            3. WEATHER & PACKING: Based explicitly on the provided live weather metadata, detail the packing essentials and appropriate practical gear to bring today.
            4. CULTURAL NORMS: Note any important dress codes or specific local ethnic/religious customs (especially for smaller towns or religious sites).
            Write this in a protective, highly practical, and peer-to-peer advisory tone. Avoid generic blurbs; make it genuinely useful for a traveler on the ground today.
            """
            insight_response = get_tab3_response(insight_prompt)
            st.markdown("---")
            st.markdown(insight_response)