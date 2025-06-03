"""
Date utilities for Excel date processing
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Union, Optional, List, Tuple
import re


class DateParser:
    """Handles date parsing and fixing for Excel files"""
    
    # Common date formats
    DATE_FORMATS = [
        '%d.%m.%Y',
        '%d. %m. %Y',
        '%d.%m.%y',
        '%d/%m/%Y',
        '%d-%m-%Y',
        '%Y-%m-%d',
        '%d. %B %Y',  # Czech month names
        '%m/%d/%Y',   # US format
        '%Y/%m/%d'
    ]
    
    # Date serial number ranges
    EXCEL_DATE_MIN = 1  # 1900-01-01
    EXCEL_DATE_MAX = 2958465  # 9999-12-31
    
    @classmethod
    def parse_date(cls, value: Union[str, float, int, datetime]) -> Optional[datetime]:
        """
        Parse date from various formats
        
        Args:
            value: Date value in various formats
            
        Returns:
            Parsed datetime or None if parsing failed
        """
        if pd.isna(value):
            return None
            
        # Already a datetime
        if isinstance(value, datetime):
            return value
            
        # Try as Excel serial number first
        if isinstance(value, (int, float)):
            return cls._parse_excel_serial(value)
            
        # Convert to string for parsing
        date_str = str(value).strip()
        
        # Try each format
        for fmt in cls.DATE_FORMATS:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
                
        # Try pandas parser as last resort
        try:
            return pd.to_datetime(date_str, dayfirst=True)
        except:
            return None
            
    @classmethod
    def _parse_excel_serial(cls, serial: Union[int, float]) -> Optional[datetime]:
        """Parse Excel serial date number"""
        try:
            if cls.EXCEL_DATE_MIN <= serial <= cls.EXCEL_DATE_MAX:
                # Excel's epoch is 1899-12-30
                return datetime(1899, 12, 30) + timedelta(days=int(serial))
        except:
            pass
        return None
        
    @classmethod
    def fix_dates_with_confidence(cls, dates: List, 
                                  confidence_threshold: float = 0.7) -> Tuple[List, List[int]]:
        """
        Fix dates in a list with confidence scoring
        
        Args:
            dates: List of date values
            confidence_threshold: Minimum confidence to apply fix
            
        Returns:
            Tuple of (fixed_dates, problematic_indices)
        """
        fixed_dates = []
        problematic_indices = []
        
        # First pass - parse all dates
        parsed_dates = []
        for i, date in enumerate(dates):
            parsed = cls.parse_date(date)
            if parsed:
                parsed_dates.append((i, parsed))
            else:
                problematic_indices.append(i)
                
        # Analyze date patterns
        if len(parsed_dates) >= 2:
            # Calculate typical interval
            intervals = []
            for i in range(1, len(parsed_dates)):
                delta = (parsed_dates[i][1] - parsed_dates[i-1][1]).days
                if 1 <= abs(delta) <= 30:  # Reasonable interval
                    intervals.append(delta)
                    
            if intervals:
                typical_interval = int(np.median(intervals))
            else:
                typical_interval = 7  # Default weekly
        else:
            typical_interval = 7
            
        # Fix problematic dates
        date_dict = dict(parsed_dates)
        
        for i, date in enumerate(dates):
            if i in date_dict:
                fixed_dates.append(date_dict[i])
            else:
                # Try to interpolate
                fixed = cls._interpolate_date(i, date_dict, typical_interval)
                if fixed:
                    fixed_dates.append(fixed)
                else:
                    fixed_dates.append(None)
                    
        return fixed_dates, problematic_indices
        
    @classmethod
    def _interpolate_date(cls, index: int, known_dates: dict, 
                         typical_interval: int) -> Optional[datetime]:
        """Interpolate missing date based on surrounding dates"""
        # Find nearest known dates
        before = None
        after = None
        
        for i in range(index - 1, -1, -1):
            if i in known_dates:
                before = (i, known_dates[i])
                break
                
        for i in range(index + 1, max(known_dates.keys()) + 1):
            if i in known_dates:
                after = (i, known_dates[i])
                break
                
        # Interpolate
        if before and after:
            # Linear interpolation
            total_gap = after[0] - before[0]
            position = index - before[0]
            total_days = (after[1] - before[1]).days
            
            interpolated_days = int(total_days * position / total_gap)
            return before[1] + timedelta(days=interpolated_days)
            
        elif before:
            # Extrapolate forward
            gap = index - before[0]
            return before[1] + timedelta(days=typical_interval * gap)
            
        elif after:
            # Extrapolate backward
            gap = after[0] - index
            return after[1] - timedelta(days=typical_interval * gap)
            
        return None
        
    @classmethod
    def format_date_for_excel(cls, date: datetime) -> str:
        """Format date for Excel output"""
        return date.strftime('%d.%m.%Y')