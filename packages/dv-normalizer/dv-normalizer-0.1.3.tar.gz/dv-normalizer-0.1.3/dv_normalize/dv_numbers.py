class DhivehiNumberConverter:
    # Dhivehi number words - standalone form (used for final digits)
    _dhivehi_digits_standalone = ['', 'އެކެއް', 'ދޭއް', 'ތިނެއް', 'ހަތަރެއް', 'ފަހެއް', 'ހައެއް', 'ހަތެއް', 'އަށެއް', 'ނުވައެއް']
    
    # Dhivehi number words - joining form (used in compound numbers)
    _dhivehi_digits_joining = ['', 'އެއް', 'ދެ', 'ތިން', 'ހަތަރު', 'ފަސް', 'ހަ', 'ހަތް', 'އަށް', 'ނުވަ']
    
    # Special numbers for 10-19
    _dhivehi_teens = [
        'ދިހައެއް',    # 10
        'އެގާރަ',      # 11
        'ބާރަ',       # 12
        'ތޭރަ',       # 13
        'ސާދަ',       # 14
        'ފަނަރަ',      # 15
        'ސޯޅަ',       # 16
        'ސަތާރަ',      # 17
        'އަށާރަ',      # 18
        'ނަވާރަ'       # 19
    ]
    
    # Special numbers for 20-29
    _dhivehi_twenties = [
        'ވިހި',       # 20
        'އެކާވީސް',    # 21
        'ބާވީސް',     # 22
        'ތޭވީސް',     # 23
        'ސައުވީސް',    # 24
        'ފަންސަވީސް',  # 25
        'ސައްބީސް',    # 26
        'ހަތާވީސް',    # 27
        'އަށާވީސް',    # 28
        'ނަވާވީސް'     # 29
    ]
    
    _dhivehi_tens = ['', 'ދިހަ', 'ވިހި', 'ތިރީސް', 'ސާޅީސް', 'ފަންސާސް', 'ފަސްދޮޅަސް', 'ހަތްދިހަ', 'އައްޑިހަ', 'ނުވަދިހަ']
    
    # Enhanced magnitude naming with better handling
    _dhivehi_magnitudes = ['', 'ސަތޭކަ', 'ހާސް', 'ލައްކަ', 'މިލިއަން', 'ބިލިއަން', 'ޓްރިލިއަން']
    
    # Special forms for hundreds - REMOVED as we'll handle this differently
    
    @classmethod
    def convert(cls, number: int) -> str:
        """
        Convert a number to its Dhivehi text representation with correct word forms.
        
        Args:
            number (int): The number to convert
            - For numbers <= 999,999,999,999: Returns full Dhivehi word representation
            - For numbers > 999,999,999,999: Returns each digit as a separate Dhivehi word
            
        Returns:
            str: The Dhivehi text representation of the number
        """
        # Handle negative numbers right at the start
        is_negative = number < 0
        
        if is_negative:
            number = abs(number)
        
        if number == 0:
            return "ސުމެއް"
        
        # For numbers larger than 1 trillion, convert each digit separately
        if number > 999999999999:
            # Convert number to string and process each digit
            digits = str(number)
            result = []
            for digit in digits:
                # Convert each digit to its standalone form
                result.append(cls._dhivehi_digits_standalone[int(digit)])
            final_result = ' '.join(result)
            return 'މައިނަސް ' + final_result if is_negative else final_result
        
        # For single-digit numbers (1-9), directly return standalone form
        if 1 <= number <= 9:
            result = cls._dhivehi_digits_standalone[number]
            return 'މައިނަސް ' + result if is_negative else result
        
        # For teen numbers (10-19), return the special form
        if 10 <= number <= 19:
            result = cls._dhivehi_teens[number - 10]
            return 'މައިނަސް ' + result if is_negative else result
        
        # For twenty numbers (20-29), return the special form
        if 20 <= number <= 29:
            result = cls._dhivehi_twenties[number - 20]
            return 'މައިނަސް ' + result if is_negative else result

        # Special case for 100,000 and 200,000
        if number == 100000:
            result = "އެއް ލައްކަ"
            return 'މައިނަސް ' + result if is_negative else result
        elif number == 200000:
            result = "ދެ ލައްކަ"
            return 'މައިނަސް ' + result if is_negative else result

        # For larger numbers, split into groups and apply magnitudes
        words = []
        
        # Process billions (if any)
        billions = number // 1000000000
        if billions > 0:
            words.append(cls._convert_three_digit_group(billions, True) + " " + cls._dhivehi_magnitudes[5])
            number %= 1000000000
        
        # Process millions (if any)
        millions = number // 1000000
        if millions > 0:
            words.append(cls._convert_three_digit_group(millions, True) + " " + cls._dhivehi_magnitudes[4])
            number %= 1000000
        
        # Process hundred thousands (lakhs) (if any)
        lakhs = number // 100000
        if lakhs > 0:
            words.append(cls._convert_three_digit_group(lakhs, True) + " " + cls._dhivehi_magnitudes[3])
            number %= 100000
        
        # Process thousands (if any)
        thousands = number // 1000
        if thousands > 0:
            words.append(cls._convert_three_digit_group(thousands, True) + " " + cls._dhivehi_magnitudes[2])
            number %= 1000
        
        # Process the remaining number (1-999)
        if number > 0:
            words.append(cls._convert_three_digit_group(number, False))
        
        # Join all parts with spaces
        final_result = ' '.join(words)
        
        # Add negative sign if needed
        if is_negative:
            final_result = 'މައިނަސް ' + final_result
        
        return final_result

    @classmethod
    def _convert_three_digit_group(cls, num: int, is_magnitude_prefix: bool = False) -> str:
        """Convert a 3-digit group (1-999)"""
        if num == 0:
            return ''
        
        result = []
        
        # Handle hundreds
        hundreds = num // 100
        if hundreds > 0:
            # Handle hundreds with proper prefix
            if hundreds == 1:
                result.append("އެއް ސަތޭކަ")
            elif hundreds == 2:
                result.append("ދުވިސައްތަ")
            elif hundreds == 3:
                result.append("ތިން ސަތޭކަ")
            elif hundreds == 4:
                result.append("ހަތަރު ސަތޭކަ")
            elif hundreds == 5:
                result.append("ފަސް ސަތޭކަ")
            elif hundreds == 6:
                result.append("ހަ ސަތޭކަ")
            elif hundreds == 7:
                result.append("ހަތް ސަތޭކަ")
            elif hundreds == 8:
                result.append("އަށް ސަތޭކަ")
            elif hundreds == 9:
                result.append("ނުވަ ސަތޭކަ")
                
            num %= 100
        
        # If nothing left, return just the hundreds
        if num == 0:
            return ' '.join(result)
        
        # Handle teens (10-19)
        if 10 <= num <= 19:
            result.append(cls._dhivehi_teens[num - 10])
            return ' '.join(result)
        
        # Handle 20-29
        if 20 <= num <= 29:
            result.append(cls._dhivehi_twenties[num - 20])
            return ' '.join(result)
        
        # Handle other tens and units
        tens = num // 10
        units = num % 10
        
        if tens > 0:
            result.append(cls._dhivehi_tens[tens])
        
        if units > 0:
            # Use joining form when it's a magnitude prefix (thousands, millions, etc.)
            # Use standalone form only for the final digit in the entire number
            if is_magnitude_prefix:
                result.append(cls._dhivehi_digits_joining[units])
            else:
                # This is the final digit of the entire number
                result.append(cls._dhivehi_digits_standalone[units])
        
        return ' '.join(result)
