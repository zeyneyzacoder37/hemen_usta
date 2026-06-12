# HemenUsta - CS50x Final Project

### Project Video Tour:[ https://youtu.be/gE7t-5mnKe8](https://youtu.be/S5mgkoHd1I0?si=98jg1BCbAD_PfMgF)

## Description:
HemenUsta is a web-based platform designed to connect local craftsmen (like plumbers, electricians, painters) with customers in their neighborhoods. It solves the real-world problem of finding trusted technical help quickly.

Users can browse featured experts, use the advanced search bar to search for specific crafts, or filter craftsmen by their cities and districts (such as Istanbul, Ankara, Kastamonu, Cekmekoy). Craftsmen can also register to the platform, log in, and manage their own profile dashboard to post their recent works, descriptions, and pricing details.

## Technical Details:
- **Backend:** Python with Flask framework.
- **Database:** SQLite3 for managing user authentication, sessions, and craftsman data.
- **Frontend:** HTML5, CSS3 (Custom responsive styling), Bootstrap 5, and FontAwesome icons.
- **Deployment:** Hosted live on Render.com with full Git synchronization.
- **Security:** Password hashing managed securely via `werkzeug.security`.

## File Structure:
- `app.py`: The main controller holding all application routes, search queries, and database initialization.
- `hemenusta.db`: SQLite database holding user and jobs tables.
- `templates/`: Directory containing HTML views (`anasayfa.html`, `login.html`, `register.html`, `panel.html`).
- `static/`: Contains uploaded job photos and local design assets.

## How to Run:
1. Ensure you have Python installed.
2. Install dependencies: `pip install flask werkzeug`
3. Run the application: `python app.py`
4. Access the site at `http://127.0.0.1:5000`
