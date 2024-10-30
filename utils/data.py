import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional
from geopy.distance import geodesic

class CoolingCenterData:
    def __init__(self, csv_path: str = 'cooling_center_data.csv'):
        """Initialize the CoolingCenterData class with CSV data"""
        # Read CSV file
        self.df = pd.read_csv(csv_path)
        
        # Clean and process coordinates
        self.df['coordinates'] = self.df['coordinates'].apply(self._parse_coordinates)
        self.df[['lat', 'lng']] = pd.DataFrame(
            self.df['coordinates'].tolist(), 
            index=self.df.index
        )
        
        # Convert features from string to list
        #self.df['features'] = self.df['features'].apply(
            #lambda x: [] if pd.isna(x) else [
                #f.strip().strip("'") for f in x.strip('[]"\'').split(',')
            #]
        #)
        # Convert features from string to list
        self.df['features'] = self.df['features'].apply(
            lambda x: x.split(',') if isinstance(x, str) else []
        )

    def _parse_coordinates(self, coord_str: str) -> tuple:
        """Parse coordinates string into tuple of floats"""
        try:
            lat, lng = map(float, coord_str.split(','))
            return (lat, lng)
        except Exception as e:
            print(f"Error parsing coordinates {coord_str}: {e}")
            return (0, 0)

    #def _parse_hours(self, hours_str: str) -> dict:
        """Parse hours string into structured format"""
        if pd.isna(hours_str):
            return {}
            
        hours_dict = {}
        # Remove extra quotes and split by semicolon
        hours_list = hours_str.strip('"\'').split(';')
        
        for hour in hours_list:
            if ':' in hour:
                day, time = hour.split(':', 1)
                hours_dict[day.strip()] = time.strip()
        
        return hours_dict

    def _is_center_open(self, hours_str: str) -> bool:
        """Check if a center is currently open"""
        if pd.isna(hours_str):
            return False

        try:
            now = datetime.now()
            current_day = now.strftime('%a').upper()

            # Split the hours string by semicolon to get each day's hours
            days_hours = [h.strip() for h in hours_str.split(';')]
            
            # Find current day's hours
            current_day_hours = None
            for day_hour in days_hours:
                if day_hour.startswith(current_day):
                    current_day_hours = day_hour
                    break
            
            if not current_day_hours:
                return False

            # Get the hours part after the colon
            _, hours = current_day_hours.split(':', 1)
            
            if hours.strip() == 'CLOSED':
                return False

            # Parse opening and closing times
            open_str, close_str = hours.strip().split('-')
            
            # Convert to datetime objects for comparison
            current_time = now.strftime("%I:%M%p")
            current_time = datetime.strptime(current_time, "%I:%M%p")
            
            open_time = datetime.strptime(open_str.strip(), "%I:%M%p")
            close_time = datetime.strptime(close_str.strip(), "%I:%M%p")
            
            # Check if current time is within opening hours
            return open_time <= current_time <= close_time

        except Exception as e:
            print(f"Error checking hours {hours_str}: {e}")
            return False

    def get_all_centers(self) -> pd.DataFrame:
        """Get only currently open centers"""
        centers = self.df.copy()
        centers['is_open'] = centers['hours'].apply(self._is_center_open)
        return centers[centers['is_open']]

    def get_nearest_centers(self, 
                          lat: float, 
                          lng: float, 
                          max_distance: float = 5.0,
                          limit: int = None,
                          show_only_open: bool = False) -> pd.DataFrame:
        """
        Get nearest cooling centers within specified distance
        
        Args:
            lat (float): User latitude
            lng (float): User longitude
            max_distance (float): Maximum distance in miles
            limit (int): Maximum number of results to return
            show_only_open (bool): Whether to show only currently open centers
        """
        centers = self.df.copy()
        
        # Calculate distances
        centers['distance'] = centers.apply(
            lambda row: self._calculate_distance(
                lat, lng, row['lat'], row['lng']
            ),
            axis=1
        )
        
        # Filter by distance
        centers = centers[centers['distance'] <= max_distance]
        
        # Add open/closed status
        centers['is_open'] = centers['hours'].apply(self._is_center_open)
        
        # Filter for only open centers if requested
        if show_only_open:
            centers = centers[centers['is_open']]
        
        # Sort by distance
        centers = centers.sort_values('distance')
        
        # Limit results if specified
        if limit:
            centers = centers.head(limit)
            
        return centers

    def _calculate_distance(self, 
                          lat1: float, 
                          lng1: float, 
                          lat2: float, 
                          lng2: float) -> float:
        """Calculate distance between two points in miles"""
        return geodesic((lat1, lng1), (lat2, lng2)).miles

    def get_centers_by_type(self, center_types: List[str]) -> pd.DataFrame:
        """Get centers of specific types"""
        return self.df[self.df['type'].isin(center_types)]

    def get_open_centers(self) -> pd.DataFrame:
        """Get only currently open centers"""
        return self.df[self.df['hours'].apply(self._is_center_open)]
