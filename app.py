import streamlit as st
from streamlit_folium import st_folium
from utils.maps import MapService
from utils.data import CoolingCenterData
from datetime import datetime

class CoolingCenterApp:
    def __init__(self):
        """Initialize app services and configuration"""
        # Initialize services
        self.map_service = MapService()
        self.data_service = CoolingCenterData()
        
        # Set page config
        st.set_page_config(
            page_title="Seattle Cool Finder",
            page_icon="🌡️",
            layout="wide"
        )
        
        # Initialize session state
        if 'user_location' not in st.session_state:
            st.session_state.user_location = None
        if 'selected_center' not in st.session_state:
            st.session_state.selected_center = None

    def render_header(self):
        """Render app header and description"""
        st.title("Seattle Cool Finder 🌡️")
        st.markdown("""
        Find your nearest cooling center in Seattle during hot weather.
        These locations provide air conditioning and a safe space to stay cool.
        """)

    def render_sidebar(self):
        """Render sidebar with filters and options"""
        with st.sidebar:
            st.header("Filter Options")
            
            # Distance filter
            max_distance = st.slider(
                "Maximum Distance (miles)",
                min_value=1,
                max_value=10,
                value=5
            )
            
            # Type filter
            center_types = st.multiselect(
                "Center Types",
                ["Community Center", "Library", "Event Hall"],
                default=["Community Center", "Library", "Event Hall"]
            )
            
            # Feature filters
            show_only_open = st.checkbox("Show Only Open Centers", value=True)
            
            return max_distance, center_types, show_only_open

    def get_user_location(self):
        """Handle user location input"""
        col1, col2 = st.columns([3, 1])
        
        with col1:
            address = st.text_input(
                "Enter your address in Seattle:",
                placeholder="123 Main St, Seattle, WA"
            )
        
        with col2:
            use_current = st.button("📍 Use My Location")
        
        if address:
            location = self.map_service.geocode_address(address)
            if location:
                st.session_state.user_location = location
                return True
        
        if use_current:
            # For demo, use downtown Seattle
            st.session_state.user_location = (47.6062, -122.3321)
            return True
            
        return False

    def display_map(self, centers_df):
        """Display map with cooling centers"""
        # Create base map
        m = self.map_service.create_base_map()
        
        # Add user location if available
        if st.session_state.user_location:
            m = self.map_service.add_user_marker(
                m, 
                st.session_state.user_location
            )
        
        # Add cooling center markers
        m = self.map_service.add_cooling_center_markers(
            m,
            centers_df.to_dict('records')
        )
        
        # Add route if center is selected
        if st.session_state.user_location and st.session_state.selected_center:
            center = centers_df[
                centers_df['name'] == st.session_state.selected_center
            ].iloc[0]
            destination = (center['lat'], center['lng'])
            m = self.map_service.add_route_to_map(
                m,
                st.session_state.user_location,
                destination
            )
        
        # Display map
        st_folium(m, width=800, height=500)

    def display_center_list(self, centers_df):
        """Display list of cooling centers"""
        st.subheader("Nearby Cooling Centers")
        
        if centers_df.empty:
            st.warning("No cooling centers found within the selected distance.")
            return
        
        for _, center in centers_df.iterrows():
            with st.expander(
                f"🏢 {center['name']} ({center['distance']:.1f} mi)"
            ):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.write(f"📍 **Address:** {center['address']}")
                    st.write(f"⏰ **Hours:** {center['hours']}")
                    st.write(f"🏷️ **Type:** {center['type']}")
                    st.write("✨ **Features:**")
                    for feature in center['features']:
                        st.write(f"  • {feature}")
                    if center.get('notes'):
                        st.write(f"📝 **Notes:** {center['notes']}")
                
                with col2:
                    if st.button("Get Directions", key=center['name']):
                        st.session_state.selected_center = center['name']
                    
                    status = "🟢 Open" if self.data_service._is_center_open(center['hours']) else "🔴 Closed"
                    st.write(f"Status: {status}")

    def run(self):
        """Main app execution"""
        self.render_header()
        
        # Get filters from sidebar
        max_distance, center_types, show_only_open = self.render_sidebar()
        
        # Get user location
        has_location = self.get_user_location()
        
        if has_location:
            # Get filtered centers
            centers = self.data_service.get_nearest_centers(
                st.session_state.user_location[0],
                st.session_state.user_location[1],
                max_distance=max_distance
            )
            
            # Apply filters
            if center_types:
                centers = centers[centers['type'].isin(center_types)]
            if show_only_open:
                centers = centers[centers['hours'].apply(self.data_service._is_center_open)]
            
            # Display results
            if not centers.empty:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    self.display_map(centers)
                
                with col2:
                    self.display_center_list(centers)
            else:
                st.warning("No cooling centers found matching your criteria.")
        else:
            st.info("👆 Enter your address to find nearby cooling centers.")
            
            # Show all centers on map
            all_centers = self.data_service.get_all_centers()
            self.display_map(all_centers)

def main():
    try:
        app = CoolingCenterApp()
        app.run()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        if st.checkbox("Show error details"):
            st.exception(e)

if __name__ == "__main__":
    main()