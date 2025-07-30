class DhivehiTimeConverter:
    # Number words dictionaries
    _number_words_standalone = {
        0: "ސުމެއް",
        1: "އެކެއް",
        2: "ދޭއް", 
        3: "ތިނެއް",
        4: "ހަތަރެއް",
        5: "ފަހެއް",
        6: "ހައެއް",
        7: "ހަތެއް",
        8: "އަށެއް",
        9: "ނުވައެއް",
    }
    
    _number_words_joining = {
        0: "ސުން",
        1: "އެއް",
        2: "ދެ",
        3: "ތިން", 
        4: "ހަތަރު",
        5: "ފަސް",
        6: "ހަ",
        7: "ހަތް",
        8: "އަށް",
        9: "ނުވަ",
        10: "ދިހަ",
        11: "އެގާރަ",
        12: "ބާރަ",
        13: "ތޭރަ",
        14: "ސާދަ",
        15: "ފަނަރަ",
        16: "ސޯޅަ",
        17: "ސަތާރަ",
        18: "އަށާރަ",
        19: "ނަވާރަ",
        20: "ވިހި",
        21: "އެކާވީސް",
        22: "ބާވީސް",
        23: "ތޭވީސް",
        24: "ސައުވީސް",  # Added missing numbers 24-29
        25: "ފަންސަވީސް",
        26: "ސައްބީސް",
        27: "ހަތާވީސް",
        28: "އަށާވީސް",
        29: "ނަވާވީސް"
    }
    
    _tens_words = {
        0: "",
        1: "ދިހަ",
        2: "ވިހި",
        3: "ތިރީސް",
        4: "ސާޅީސް", 
        5: "ފަންސާސް",
        6: "ފަސްދޮޅަސް"
    }

    @classmethod
    def convert(cls, time_str):
        """
        Convert time string to Dhivehi text representation.
        Auto-detects 12/24-hour format based on input hour value.
        
        Args:
            time_str (str): Time string in format "HH:MM" (24-hour or 12-hour format)
            
        Returns:
            str: The Dhivehi text representation of the time
        """
        # Parse the time string
        try:
            hours, minutes = map(int, time_str.split(':'))
            
            # Validate time format
            if not (0 <= hours <= 23 and 0 <= minutes <= 59):
                raise ValueError("Invalid time format")
        except:
            return "Invalid time format. Please use HH:MM format (e.g., 14:30 or 01:05)."
        
        # Auto-detect format: if hours > 12, use 24-hour format, otherwise use 12-hour
        use_12hour = hours <= 12
        
        # If 24-hour format is detected and hours > 12, keep as is
        # If 12-hour format is used, adjust midnight (00:00) to 12
        if use_12hour and hours == 0:
            hours = 12
        
        # Handle special case for 00:00
        if hours == 0 and minutes == 0:
            if use_12hour:
                return "ބާރަ ގަޑި ސުމެއް"  # 12 o'clock zero
            else:
                return "ސުން ގަޑި ސުމެއް"  # 0 o'clock zero
        
        # Convert hours to Dhivehi
        hours_text = cls._number_words_joining.get(hours, "")
        
        # Convert minutes to Dhivehi
        if minutes == 0:
            minutes_text = "ސުމެއް"  # Zero/null for minutes
        elif minutes < 10:
            minutes_text = cls._number_words_standalone[minutes]  # Use standalone form for final digits
        elif minutes < 20:
            if minutes == 10:
                minutes_text = "ދިހައެއް"  # Special case for 10
            else:
                minutes_text = cls._number_words_joining[minutes]  # Use special words for 11-19
        elif minutes < 30:
            tens = minutes // 10
            units = minutes % 10
            if units == 0:
                minutes_text = cls._tens_words[tens]
            else:
                # Use the special words for 21-29 if they exist in the dictionary
                minutes_text = cls._number_words_joining.get(minutes, f"{cls._tens_words[tens]} {cls._number_words_standalone[units]}")
        else:
            tens = minutes // 10
            units = minutes % 10
            if units == 0:
                minutes_text = cls._tens_words[tens]
            else:
                minutes_text = f"{cls._tens_words[tens]} {cls._number_words_standalone[units]}"  # Use standalone form for final digits
        
        # Combine parts - simple format
        time_text = f"{hours_text} ގަޑި {minutes_text}"
        
        return time_text

