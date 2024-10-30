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
        self.df['features'] = self.df['features'].apply(
            lambda x: [] if pd.isna(x) else [
                f.strip().strip("'") for f in x.strip('[]"\'').split(',')
            ]
        )

    def _parse_coordinates(self, coord_str: str) -> tuple:
        """Parse coordinates string into tuple of floats"""
        try:
            lat, lng = map(float, coord_str.split(','))
            return (lat, lng)
        except Exception as e:
            print(f"Error parsing coordinates {coord_str}: {e}")
            return (0, 0)

    def _parse_hours(self, hours_str: str) -> dict:
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
        """
        Check if a center is currently open based on hours string
        Example hours_str format: "MON:9:00AM-5:00PM;TUE:9:00AM-5:00PM"
        """
        if pd.isna(hours_str) or hours_str == '':
            return False

        try:
            # Get current day and time
            now = datetime.now()
            current_day = now.strftime('%a').upper()  # Get current day abbreviation (MON, TUE, etc.)

            # Parse hours string into dictionary
            hours_dict = {}
            days = hours_str.strip('"\'').split(';')
            for day_hours in days:
                if ':' in day_hours:
                    day, hours = day_hours.split(':', 1)
                    hours_dict[day.strip()] = hours.strip()

            # Check if we have hours for current day
            if current_day not in hours_dict:
                return False

            # Get today's hours
            today_hours = hours_dict[current_day]
            if today_hours == 'CLOSED':
                return False

            # Split into open and close times
            open_time_str, close_time_str = today_hours.split('-')

            # Convert current time to minutes since midnight
            current_minutes = now.hour * 60 + now.minute

            # Convert opening time to minutes since midnight
            open_time = datetime.strptime(open_time_str.strip(), '%I:%M%p')
            open_minutes = open_time.hour * 60 + open_time.minute

            # Convert closing time to minutes since midnight
            close_time = datetime.strptime(close_time_str.strip(), '%I:%M%p')
            close_minutes = close_time.hour * 60 + close_time.minute

            # Check if current time is within opening hours
            return open_minutes <= current_minutes <= close_minutes

        except Exception as e:
            print(f"Error checking hours for {hours_str}: {e}")
            return False
    def get_all_centers(self) -> pd.DataFrame:
        """Get all cooling centers"""
        return self.df

    def get_nearest_centers(self, 
                          lat: float, 
                          lng: float, 
                          max_distance: float = 5.0,
                          limit: int = None,
                          show_only_open: bool = False) -> pd.DataFrame:
        """Get nearest cooling centers within specified distance
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
        
        # Add open/closed status
        centers['is_open'] = centers['hours'].apply(self._is_center_open)
        
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
        centers = self.df.copy()
        centers['is_open'] = centers['hours'].apply(self._is_center_open)
        return centers[centers['is_open']]
