# 🍍 PineApple — AI-Powered Automated Blogger

**PineApple** is a smart automation project that combines **AI**, **data**, and **code** to create and publish daily content - fully hands-off.

Every morning, PineApple:
1. Fetches Indian personalities whose birthdays are today using the **Wikidata SPARQL API**  
2. Calculates an **importance score** (based on Wikipedia reach, awards, and article length)  
3. Generates an engaging article with **Google Gemini AI**  
4. Automatically publishes it on **Blogger** - no human required 😎  

---

## 🧠 Tech Stack
| Component | Purpose |
|------------|----------|
| **Python** | Core automation & workflow logic |
| **Wikidata SPARQL API** | Fetches public data of Indian personalities |
| **Google Gemini AI** | Generates high-quality biography content |
| **Blogger API** | Publishes the content automatically |
| **GitHub Actions / Google Cloud Run** | For scheduled automation & hosting |

---

## ⚙️ Key Features
- 🔁 **Fully Automated** – Runs daily, end-to-end without manual triggers  
- 🧮 **AI-Driven Scoring** – Determines the top personalities intelligently  
- ✍️ **Smart Article Generation** – Natural-sounding AI-written bios  
- ☁️ **Auto Publishing** – Directly posts to your Blogger site  
- 💾 **Data Transparency** – Uses only open & public data sources  

---

## 🧩 Setup (Run Locally)

```bash
# 1️⃣ Clone the repository
git clone https://github.com/<your-username>/PineApple.git
cd PineApple

# 2️⃣ Install dependencies
pip install -r requirements.txt

# 3️⃣ Add your Google API credentials file
# Place credentials.json in the project root (do NOT upload this to GitHub)

# 4️⃣ Run the bot manually
python main.py
