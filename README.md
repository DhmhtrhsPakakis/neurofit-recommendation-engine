# 🎨 NeuroFit Art Recommender

Welcome to **NeuroFit**, your personal smart art gallery! NeuroFit is not just an app for viewing paintings; it's an Artificial Intelligence (AI) engine that "learns" your aesthetics and recommends artworks tailored to your taste.

## 🌟 How It Works
1. **Discovery:** The app connects to the Art Institute of Chicago API and brings thousands of artworks directly to your screen.
2. **Rating (Like / Dislike):** As you view the paintings, click **👍 (Like)** on the ones you enjoy and **👎 (Dislike)** on the ones that don't match your taste.
3. **Personalization:** Once you gather a few ratings, the Artificial Intelligence (NeuroFit) takes over. In the background, it scans every new artwork and **automatically hides** those that are similar to your Dislikes, recommending only the best pieces for you!

## 🚀 Key Features
* **Infinite Scroll Gallery:** Browse an endless stream of artworks that dynamically refreshes in the background (without freezing).
* **See Preferences:** A dedicated window where you can see all the artworks you have loved (Likes) or rejected (Dislikes) in one place.
* **Rejected Artworks:** Wondering what the AI "filtered out" for you? In this tab, you can transparently see all the artworks rejected by the algorithm because they didn't fit your profile.
* **View Full Webpage:** With a single click (🔍 View Web), you are redirected to the museum's official page to view the artwork in high resolution and read its history.

## 🛠️ Installation & Execution Guide
1. Ensure you have Python 3.9+ installed.
2. Install the required packages by running:
   ```bash
   pip install -r requirements.txt