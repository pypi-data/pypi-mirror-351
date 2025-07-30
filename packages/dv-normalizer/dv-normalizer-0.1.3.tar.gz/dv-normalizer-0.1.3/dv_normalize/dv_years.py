class DhivehiYearConverter:
    # Constants for number words
    DIGITS_JOINING = ['', 'އެއް', 'ދޭއް', 'ތިން', 'ހަތަރު', 'ފަސް', 'ހަ', 'ހަތް', 'އަށް', 'ނުވަ']
    TENS = ['', 'ދިހަ', 'ވިހި', 'ތިރީސް', 'ސާޅީސް', 'ފަންސާސް', 'ފަސްދޮޅަސް', 'ހަތްދިހަ', 'އައްޑިހަ', 'ނުވަދިހަ']
    TEENS = ['ދިހައެއް', 'އެގާރަ', 'ބާރަ', 'ތޭރަ', 'ސާދަ', 'ފަނަރަ', 'ސޯޅަ', 'ސަތާރަ', 'އަށާރަ', 'ނަވާރަ']
    TWENTIES = ['ވިހި', 'އެކާވީސް', 'ބާވީސް', 'ތޭވީސް', 'ސައުވީސް', 'ފަންސަވީސް', 'ސައްބީސް', 'ހަތާވީސް', 'އަށާވީސް', 'ނަވާވީސް']
    
    @classmethod
    def convert(cls, year):
        """
        Convert a year to its Dhivehi text representation using the proper year format.
        
        Args:
            year (int): The year to convert
            
        Returns:
            str: The Dhivehi text representation of the year
        """
        # Handle negative years (BCE)
        is_bce = year < 0
        if is_bce:
            year = abs(year)
        
        # Special case for years < 100 (rare but possible)
        if year < 100:
            return cls._convert_under_100(year, is_bce)
        
        # For years 2000 and above
        if year >= 2000:
            return cls._convert_2000_plus(year)
            
        # For years 1000-1999 
        if year >= 1000:
            return cls._convert_1000_to_1999(year)
            
        # For years under 1000
        return cls._convert_under_1000(year, is_bce)

    @classmethod
    def _convert_under_100(cls, year, is_bce):
        """Convert years under 100 to Dhivehi."""
        if year < 10:
            result = cls.DIGITS_JOINING[year]
        elif year < 20:
            result = cls.TEENS[year - 10]
        elif year < 30:
            result = cls.TWENTIES[year - 20]
        else:
            tens_digit = year // 10
            units_digit = year % 10
            
            if units_digit == 0:
                result = cls.TENS[tens_digit]
            else:
                result = f"{cls.TENS[tens_digit]} {cls.DIGITS_JOINING[units_digit]}"
        
        return result + (" ކުރީގެ" if is_bce else "")

    @classmethod
    def _convert_under_1000(cls, year, is_bce):
        """Convert years under 1000 to Dhivehi."""
        century = year // 100
        remainder = year % 100
        
        # Get century text
        if century == 0:
            century_text = ""
        else:
            century_text = cls.DIGITS_JOINING[century] + "ސަތޭކަ"
        
        # If no remainder, return just the century
        if remainder == 0:
            return century_text + (" ކުރީގެ" if is_bce else "")
        
        # Handle remainder
        if remainder < 100:
            remainder_text = " " + cls._convert_under_100(remainder, False)  # False because BCE is handled outside
        
        return century_text + remainder_text + (" ކުރީގެ" if is_bce else "")

    @classmethod
    def _convert_2000_plus(cls, year):
        """Convert years 2000 and above to Dhivehi."""
        thousands = year // 1000
        remainder = year % 1000
        
        # Handle thousands
        if thousands == 2:
            thousands_text = "ދެހާސް"
        else:
            thousands_text = cls.DIGITS_JOINING[thousands] + "ހާސް"
        
        # If no remainder, return just the thousands
        if remainder == 0:
            return thousands_text
        
        # Handle hundreds
        hundreds = remainder // 100
        last_two_digits = remainder % 100
        
        remainder_text = ""
        
        # Add hundreds
        if hundreds > 0:
            remainder_text = " " + cls.DIGITS_JOINING[hundreds] + "ސަތޭކަ"
        
        # Add last two digits
        if last_two_digits > 0:
            remainder_text += " " + cls._convert_under_100(last_two_digits, False)  # False because BCE is handled outside
        
        return thousands_text + remainder_text

    @classmethod
    def _convert_1000_to_1999(cls, year):
        """
        Convert years 1000-1999 to Dhivehi.
        For most years we use the format "X-hundred Y" instead of "one thousand X hundred Y"
        Special case: 1000-1099 uses "one thousand" format
        """
        # For years 1000-1099, use "one thousand" format
        if 1000 <= year < 1100:
            remainder = year % 1000
            
            base = "އެއްހާސް"
            
            # If it's exactly 1000
            if remainder == 0:
                return base
                
            # For years 1001-1099
            remainder_text = " " + cls._convert_under_100(remainder, False)
            return base + remainder_text
        
        # For years 1100-1999, we use the century format
        century = (year // 100)
        last_two_digits = year % 100
        
        # Convert the century text (11-19)
        if century == 11:
            century_text = "އެގާރަސަތޭކަ"
        elif century == 12:
            century_text = "ބާރަސަތޭކަ"
        elif century == 13:
            century_text = "ތޭރަސަތޭކަ"
        elif century == 14:
            century_text = "ސާދަސަތޭކަ"
        elif century == 15:
            century_text = "ފަނަރަސަތޭކަ"
        elif century == 16:
            century_text = "ސޯޅަސަތޭކަ"
        elif century == 17:
            century_text = "ސަތާރަސަތޭކަ"
        elif century == 18:
            century_text = "އަށާރަސަތޭކަ"
        elif century == 19:
            century_text = "ނަވާރަސަތޭކަ"
        
        # If no remainder, return just the century
        if last_two_digits == 0:
            return century_text
        
        # Add last two digits
        remainder_text = " " + cls._convert_under_100(last_two_digits, False)  # False because BCE is handled outside
        
        return century_text + remainder_text