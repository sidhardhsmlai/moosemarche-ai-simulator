import streamlit as st
import json
import time
import re
import random
import string

# --- CONFIGURATION ---
st.set_page_config(page_title="Moosebot Prototype", page_icon="🫎", layout="centered")

# --- 🎨 FINAL WHATSAPP STYLE THEME (FORCE ALIGNMENT) ---
MOOSE_THEME = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Playfair+Display:wght@700&display=swap');

    :root {
        --primary-teal: #00BFA5;
        --bg-light: #F9FAFB;
        --text-dark: #111827;
        --border: #E5E7EB;
    }

    .stApp { background-color: var(--bg-light); font-family: 'Inter', sans-serif; }
    h1 { font-family: 'Playfair Display', serif !important; color: var(--text-dark) !important; font-weight: 800 !important; }

    /* USER MESSAGE (RIGHT) */
    div[data-testid="stChatMessage"]:nth-of-type(even) {
        flex-direction: row-reverse !important;
        text-align: right !important;
        background-color: transparent !important;
    }
    div[data-testid="stChatMessage"]:nth-of-type(even) div[data-testid="stMarkdownContainer"] {
        background-color: var(--primary-teal) !important;
        color: white !important;
        padding: 12px 18px !important;
        border-radius: 18px 18px 0 18px !important;
        margin-left: auto !important;
        margin-right: 10px !important;
    }
    div[data-testid="stChatMessage"]:nth-of-type(even) p { color: white !important; }

    /* BOT MESSAGE (LEFT) */
    div[data-testid="stChatMessage"]:nth-of-type(odd) {
        flex-direction: row !important;
        text-align: left !important;
        background-color: transparent !important;
    }
    div[data-testid="stChatMessage"]:nth-of-type(odd) div[data-testid="stMarkdownContainer"] {
        background-color: #FFFFFF !important;
        border: 1px solid var(--border) !important;
        color: var(--text-dark) !important;
        padding: 12px 18px !important;
        border-radius: 18px 18px 18px 0 !important;
        margin-right: auto !important;
        margin-left: 10px !important;
    }
    .stChatInput input { border-radius: 25px !important; border: 1px solid #D1D5DB !important; background-color: white !important; }
    div[data-testid="stChatMessageAvatar"] { background-color: transparent !important; }
</style>
"""
st.markdown(MOOSE_THEME, unsafe_allow_html=True)

# --- DATA LOADER ---
@st.cache_data
def load_data():
    try:
        with open('simulation_config.json', 'r') as f:
            sim_data = json.load(f)
        with open('brand_data.txt', 'r', encoding='utf-8') as f:
            brand_text = f.read()
        return sim_data, brand_text
    except FileNotFoundError:
        return None, None

sim_data, brand_text = load_data()

if not sim_data or not brand_text:
    st.error("🚨 CRITICAL ERROR: Data files not found!")
    st.stop()

# --- HELPER: ROBUST NUMBER EXTRACTOR ---
def extract_views(prompt):
    clean_prompt = prompt.lower().translate(str.maketrans('', '', string.punctuation))
    clean_prompt = re.sub(r'(\d+)\s+(\d+)', r'\1\2', clean_prompt)
    if "million" in clean_prompt:
        match = re.search(r'(\d+(?:\.\d+)?)', clean_prompt)
        if match: return int(float(match.group(1)) * 1000000)
    k_match = re.search(r'(\d+(?:\.\d+)?)k', clean_prompt)
    if k_match: return int(float(k_match.group(1)) * 1000)
    m_match = re.search(r'(\d+(?:\.\d+)?)m', clean_prompt)
    if m_match: return int(float(m_match.group(1)) * 1000000)
    numbers = re.findall(r'\d+', clean_prompt)
    if numbers: return int(max(numbers, key=int))
    return 1000

# --- HELPER: SYNONYM MAPPER ---
def expand_search_terms(prompt):
    synonyms = {
        "car": "automotive", "auto": "automotive", "vehicle": "automotive", "mechanic": "automotive",
        "fix": "home services", "repair": "home services", "clean": "home services", "plumb": "home services",
        "bread": "food", "eat": "food", "restaurant": "food", "snack": "food", "baker": "food", "dining": "food",
        "class": "education", "teach": "education", "school": "education", "learn": "education", "tutor": "education",
        "pic": "creative", "photo": "creative", "video": "creative", "design": "creative",
        "gym": "health", "workout": "health", "fitness": "health",
        "cat": "pets", "dog": "pets", "animal": "pets"
    }
    expanded_prompt = prompt
    for key, value in synonyms.items():
        if key in prompt: expanded_prompt += f" {value}"
    return expanded_prompt

# --- THE LOGIC ENGINE ---
def generate_response(prompt, history):
    raw_prompt = prompt
    prompt = prompt.lower().translate(str.maketrans('', '', string.punctuation))
    
    last_bot_msg = ""
    if len(history) > 0:
        for msg in reversed(history):
            if msg["role"] == "assistant":
                last_bot_msg = msg["content"].lower()
                break

    in_consumer_flow = "found these local vendors" in last_bot_msg or "verified vendor" in last_bot_msg or "active categories" in last_bot_msg
    in_vendor_flow = "campaign simulation" in last_bot_msg or "strategy benefit" in last_bot_msg

    # 1. AFFIRMATION HANDLER (FIXED FOR "STANDARD" / "PREMIUM")
    # We now check if specific keywords are present ANYWHERE in the prompt
    closing_keywords = ["yes", "please", "sure", "ok", "yep", "do it", "good", "deal", "go ahead", "interested", "join", "add me", "waitlist", "sign me up", "standard", "premium"]
    
    is_affirmation = any(x in prompt for x in closing_keywords)
    
    if is_affirmation:
        if in_vendor_flow:
            # Determine plan from user text, default to what they likely want
            plan_type = "Premium" if "premium" in prompt else "Standard" if "standard" in prompt else "Custom"
            ticket_id = random.randint(10000, 99999)
            return f"""
✅ **Campaign Request Logged**
> **Ticket ID:** `#MB-{ticket_id}`
> **Plan Preference:** {plan_type} Tier
> **Status:** Pushed to Sales CRM

I have alerted the team. They will audit your creative assets and contact you within 24 hours.
""", "vendor_lead"
        elif in_consumer_flow or "waitlist" in last_bot_msg:
            return "Done! ✅ You are confirmed. You are #4,201 on the Waitlist. We will notify you in Jan 2026.", "consumer_lead"

    # 2. IDENTITY RECOGNITION
    vendor_identity_keywords = ["vendor", "seller", "business", "i run a", "i own a", "i have a", "my company", "my shop", 
                                "i am a mechanic", "i am a plumber", "i am a tutor", "i am a baker", "i am a photographer", "freelancer", "contractor"]
    if any(x in prompt for x in vendor_identity_keywords):
         industry_msg = ""
         if "plumb" in prompt: industry_msg = "Plumbing companies perform excellently on our platform."
         if "food" in prompt or "bakery" in prompt: industry_msg = "Local food businesses are our top category."
         if "mechanic" in prompt or "auto" in prompt: industry_msg = "Automotive services are in high demand locally."
         return f"Welcome, Vendor! 👋\n\n{industry_msg}\n\nI can simulate an ad campaign for you.\n\n**Try asking:**\n* 'Quote for 30k views'\n* 'Budget for 1 million impressions'", "none"

    # 3. CONSUMER PRICING
    if in_consumer_flow and any(x in prompt for x in ["price", "cost", "how much", "rate", "expensive"]):
        price_info = "**Service Rates:** Vendors set their own rates (e.g. Tutors ~$40/hr, Plumbers ~$100/visit)."
        if "tutor" in last_bot_msg or "education" in last_bot_msg: price_info = "**Tutors:** Typically $30 - $60 / hr."
        elif "plumb" in last_bot_msg or "home services" in last_bot_msg: price_info = "**Plumbers:** Typically $100+ / visit."
        elif "bakery" in last_bot_msg or "food" in last_bot_msg: price_info = "**Bakeries:** Varies by item."
        elif "mechanic" in last_bot_msg or "automotive" in last_bot_msg: price_info = "**Mechanics:** Typically $90 - $120 / hr."
        return f"**Estimated Pricing:**\n{price_info}\n\n*Note: Exact menus available upon launch.*\n\n**Shall I add you to the waitlist?**", "consumer"

    # 4. SMALL TALK
    if prompt in ["thanks", "thank you", "cool", "great", "awesome", "nice"]:
        return "You're welcome! Is there anything else I can help you find or calculate?", "none"

    # 5. VENDOR LOGIC
    vendor_triggers = ["cost", "price", "ads", "advertise", "cpm", "budget", "rates", "how much", "views", "spend", "pay", "quote", "estimate", "reach"]
    if any(x in prompt for x in vendor_triggers) and not in_consumer_flow:
        views = extract_views(raw_prompt)
        cpm_std = sim_data["pricing_model"]["standard"]["cpm_cost"]
        cpm_prem = sim_data["pricing_model"]["premium"]["cpm_cost"]
        cost_std = (views / 1000) * cpm_std
        cost_prem = (views / 1000) * cpm_prem
        est_clicks = int(views * 0.012)
        est_reach = int(views * 0.85)
        return f"""
### 📊 Campaign Simulation: {views:,} Impressions

**Projected Performance:**
* **Est. Unique Reach:** ~{est_reach:,} locals
* **Est. Clicks (1.2% CTR):** ~{est_clicks:,} visits

| Tier | Budget | ROI Focus |
| :--- | :--- | :--- |
| **Standard** | **${cost_std:,.2f}** | Awareness (CPM ${cpm_std}) |
| **Premium** | **${cost_prem:,.2f}** | Conversion (CPM ${cpm_prem}) |

💡 **Strategist Recommendation:** For **{views:,} views**, I recommend **Premium** for the 'Verified Badge'.

**Action:** Shall I lock in this quote for the **Premium** tier?
""", "vendor"

    # 6. CONSUMER SEARCH
    consumer_triggers = ["find", "search", "looking", "plumber", "bakery", "tutor", "where", "need", "hire", "show", "list", "yoga", "gym", "food", "tech", "auto", "want", "have", "available", "everything", "options", "categories", "car", "dog", "fix", "repair", "mechanic", "baker"]
    if any(x in prompt for x in consumer_triggers):
        results = []
        smart_prompt = expand_search_terms(prompt)
        ignore_words = ["find", "search", "looking", "for", "a", "an", "need", "me", "show", "where", "is", "the", "hire", "list", "verified", "local", "i", "want", "like", "do", "you", "have", "what", "all", "to", "in", "at", "place", "services"]
        query_words = [w for w in smart_prompt.split() if w not in ignore_words]
        for vendor in sim_data["vendor_inventory"]:
            v_data = f"{vendor['name']} {vendor['category']} {vendor['location']}".lower()
            is_match = False
            for word in query_words:
                if len(word) > 1 and word in v_data: is_match = True
            
            if "plumb" in prompt and "home services" in v_data: is_match = True
            
            if is_match:
                verified_badge = "✅ **VERIFIED**" if vendor["verified"] else "⚠️ Unverified"
                stars = "⭐" * int(vendor['rating'])
                cat_tag = f"`{vendor['category']}`"
                results.append(f"**{vendor['name']}** {cat_tag}\n* 📍 {vendor['location']}\n* {verified_badge} | {stars} ({vendor['rating']})")
        if results:
            return "I found these local vendors in our database:\n\n" + "\n\n".join(results) + "\n\n---\n*Note: Booking active Jan 2026. Join waitlist?*", "consumer"
        else:
             categories = sorted(list(set([v["category"] for v in sim_data["vendor_inventory"]])))
             cat_list = ", ".join(categories)
             return f"I couldn't find a specific match for '{raw_prompt}'.\n\n**Here are the active categories in our simulation:**\n\n📂 {cat_list}\n\n*Try searching for one of these!*", "none"

    # F. BRAND POLICY
    if any(x in prompt for x in ["privacy", "data", "safe", "values", "mission", "trust"]):
        return f"**From our Official Policy:**\n\n> *{brand_text[:300]}...*\n\n(Source: brand_data.txt)", "brand"
    
    # H. AMBIGUITY
    if any(x in prompt for x in ["hi", "hello", "hey", "start"]):
        return "Hello! I am Moosebot. Are you a **Vendor** looking to advertise, or a **Consumer** looking for local services?", "none"

    return "I am a Prototype in Simulation Mode.\n\n**Try asking:**\n* 'Quote for 30k views'\n* 'Find a plumber'", "none"

# --- UI SETUP ---
with st.sidebar:
    st.title("🫎 Moosemarche AI")
    st.markdown("---")
    st.success("🟢 **Simulation Mode: ACTIVE**")
    st.caption("Operating on Mock Data (Offline Mode)")
    st.markdown("---")
    show_debug = st.checkbox("Show Logic (Debug)", value=False)
    if st.button("Clear Session"):
        st.session_state.messages = []; st.rerun()

st.header("Moosemarche Intelligent Assistant (BETA)")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! I am MooseBot. Are you a **Vendor** or a **Consumer**?"}]

for msg in st.session_state.messages:
    if msg["role"] == "assistant":
        with st.chat_message(msg["role"], avatar="🫎"):
            st.write(msg["content"])
    else:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant", avatar="🫎"):
        spinner_text = "Processing..."
        if "view" in prompt.lower() or "cost" in prompt.lower(): spinner_text = "🔄 Simulating Campaign ROI..."
        elif "find" in prompt.lower() or "search" in prompt.lower(): spinner_text = "🔍 Querying Vendor Database..."
            
        with st.spinner(spinner_text):
            time.sleep(0.5) 
            response_text, logic_path = generate_response(prompt, st.session_state.messages)
            st.write(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})

            if logic_path == "vendor_lead": st.toast("✅ VENDOR LEAD CAPTURED", icon="🚀")
            if logic_path == "consumer_lead": st.toast("✅ WAITLIST CONFIRMED", icon="🛡️")

            if show_debug:
                with st.expander("🛠️ Internal Logic State"):
                    st.write(f"**Intent Detected:** {logic_path.upper()}")
                    if "vendor" in logic_path: st.json(sim_data["pricing_model"])
                    elif "consumer" in logic_path: st.json(sim_data["vendor_inventory"])