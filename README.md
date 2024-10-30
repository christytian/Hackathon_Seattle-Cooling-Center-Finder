# Seattle Cooling Center Finder

A Streamlit web application to help Seattle residents find nearby cooling centers during hot weather events.

## Features

- Find nearest cooling centers based on your location
- Real-time directions and distance calculations
- Filter centers by type and operating hours
- Interactive map with detailed information
- Mobile-friendly interface

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/seattle-cooling.git
cd Hackathon_Seattle-Cooling-Center-Finder
```

2. Set up environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirement.txt
```

3. Add A Google Maps API key
   https://developers.google.com/maps/documentation/maps-static
   Create a .env file in project root and Add: GOOGLE_MAPS_API_KEY=your_api_key_here

4. Run the app

```bash
streamlit run app.py
```
