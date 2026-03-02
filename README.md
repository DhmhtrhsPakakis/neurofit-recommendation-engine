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

---

### Technical

```markdown
# ⚙️ NeuroFit Art Recommender - Technical Documentation

**NeuroFit** is an advanced Recommendation System that combines Computer Vision, Machine Learning
and an Asynchronous Graphical User Interface (GUI). The system fetches data from external APIs,
extracts features (feature embeddings) via Deep Learning,
and uses similarity algorithms to filter content in real-time.

## 🏗️ System Architecture

The project follows a decoupled architecture (UI and Backend separation), based on 4 main pillars:

### 1. Asynchronous Data Pipeline (Background Threading)
To prevent the UI from freezing during image downloads, the application uses a `DataPipeline`running on a separate Daemon Thread.
* Communicates with the API Scraper to download pages of artworks in batches.
* Forwards artworks to the Recommender for approval.
* Routes the results into Thread-safe Queues (`queue.Queue`) for smooth UI updates (Producer-Consumer pattern).

### 2. NeuroFit AI Recommender Engine
The "heart" of the system. It works as follows:
* **Feature Extraction:** Each downloaded image passes through a pre-trained convolutional neural network (**ResNet50**).
The network removes the final classification layers and extracts a dense feature vector (Embedding Vector).
* **Cosine Similarity Check:** The system uses the `scikit-learn` library to calculate the Cosine Similarity between
the new vector and the vectors of artworks the user has Liked or Disliked. If the new artwork is too similar to the Dislikes,
it is automatically rejected.

### 3. Database & Memory (SQLite & Local Caching)
Data management has been optimized to minimize Network Requests:
* **SQLite Database (`art_recommender.db`):** A relational database with two tables (`ARTWORKS` & `PREFERENCES`)
with strict Foreign Keys. The system permanently stores Numpy Embeddings (as JSON strings) and metadata *only* when
the user interacts (Like/Dislike), saving disk space.
* **Local Image Cache (`img_cache/`):** Images are stored locally.
The GUI loads them directly from the disk using the `Pillow` library, preventing HTTP 403 Forbidden errors and API Timeouts.
* **UI State Cache (`ui_preferences.json`):** Whitelist-based JSON caching (saves only strings/ints,
ignoring numpy arrays) for instant loading of User Preferences in modal windows.

### 4. Graphical User Interface (CustomTkinter)
The GUI was designed with the `CustomTkinter` library, offering a modern Dark Mode UI.
* **Lazy Loading & Pagination:** The gallery reads batches from the Pipeline and
loads cards (`ArtCard`) dynamically.
* **Memory Management:** Implementation of strict reference control (garbage collection overrides)
to keep images in memory (Tkinter PhotoImage reference bug bypass).
* **Cross-window Scrolling:** Dynamic management of MouseWheel events depending
on which TopLevel modal (Preferences / Rejected) has the focus.

## 🛠️ Technologies & Tools
* **Language:** Python 3.11
* **Machine Learning / AI:** Scikit-Learn (Cosine Similarity), NumPy, Scipy, [ResNet50].
* **GUI:** CustomTkinter (Tkinter wrapper).
* **Database:** SQLite3 (Built-in).
* **Network & Image Processing:** Requests, Pillow (PIL).

## 🚀 Future Work
* Ability to extract the "Artistic Profile" (Clustering Likes to find the user's favorite movement, e.g., Impressionism).
* Multi-threading in the Scraper for parallel image downloading.