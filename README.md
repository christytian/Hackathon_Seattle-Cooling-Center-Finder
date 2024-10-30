# Seattle Cooling Centers Finder

A Streamlit web application helping Seattle residents locate nearby cooling centers during hot weather events.

## Features

- **Location-Based Search**: Find nearest cooling centers based on your current location
- **Real-Time Navigation**: Get instant directions and distance calculations
- **Advanced Filtering**: Sort centers by type (libraries, community centers, etc.) and hours of operation
- **Interactive Map**: Visual interface showing all centers with detailed popup information
- **Mobile-Optimized**: Fully responsive design for easy access on phones and tablets

## Installation

```bash
# Clone repository
git clone https://github.com/christytian/Hackathon_Seattle-Cooling-Center-Finder/blob/main/utils/data.py

# Install dependencies
cd seattle-cooling-centers
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Allow location access when prompted or enter your address manually
3. View nearby cooling centers on the map
4. Use filters to refine your search
5. Click on any center for detailed information and directions

## Requirements

- Python 3.8+
- Streamlit
- Pandas
- Folium
- Requests
- GeoPy

## Data Sources

- Seattle Open Data Portal
- King County GIS Data
- OpenStreetMap

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License. See [LICENSE](LICENSE) for details.

## Support

For issues or questions:
- Open a GitHub issue
- Contact: cooling-centers@seattle.gov

## Acknowledgments

- Seattle Office of Emergency Management
- King County Emergency Management
- Seattle Public Libraries
