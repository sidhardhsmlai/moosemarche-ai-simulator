# ?? Moosebot: The Future-State AdTech Simulator

> **Status:** Prototype (V1.0)
> **Engine:** Logic-Based Router (Regex + Context Awareness)
> **Goal:** Simulating 'Day 1' Operations for Moosemarche

## ?? The Challenge
Moosemarche is currently in **Waitlist Mode**, meaning there is no live user data or inventory to scrape. 

Instead of building a static FAQ bot, I engineered a **Future-State Simulator**. This prototype mimics the backend logic of the platform as if it were fully live, demonstrating how the ML pipeline will handle **Vendor ROI calculations** and **Consumer Trust signals**.

## ?? The Architecture (Logic Router)
The bot does not rely on black-box hallucinations. It uses a deterministic **State Machine** to route user intent:

1.  **Vendor Logic (The Strategist):**
    * Detects business owners ("I run a bakery").
    * Parses natural language numbers ("30k views", "1.5 million").
    * **Simulation:** Calculates estimated Cost, Reach, and CTR based on industry-standard CPMs.
    * **Upsell Engine:** Comparison table for Standard vs. Premium tiers.

2.  **Consumer Logic (The Marketplace):**
    * **Fuzzy Search:** Matches intents like "car" to "Automotive" and "fix" to "Home Services".
    * **Context Guard:** Distinguishes between "Ad Price" (B2B) and "Service Rates" (B2C) based on conversation history.
    * **Trust Signals:** Prioritizes verified vendors in search results.

3.  **Identity Layer:**
    * Recognizes trade-specific identities ("I am a mechanic") and adapts the welcome message instantly.

## ??? Tech Stack
* **Frontend:** Streamlit (Python)
* **Logic:** Regex-based NLP & Context State Management
* **Data:** JSON-based Simulation Engine (simulation_config.json)
* **Knowledge Base:** Text Retrieval (rand_data.txt)

## ?? How to Run Locally
1.  Clone the repository.
2.  Install requirements:
    `ash
    pip install -r requirements.txt
    `
3.  Run the engine:
    `ash
    streamlit run app.py
    `

## ?? Usage Examples
* **Vendor:** _"Quote for 20k views"_ ? Returns CPM Table.
* **Consumer:** _"Find a plumber"_ ? Returns Verified Listings.
* **Context:** _"Price?"_ ? Detects context and returns Service Rates (not Ad rates).

---
*Built for the Moosemarche Engineering Team.*
