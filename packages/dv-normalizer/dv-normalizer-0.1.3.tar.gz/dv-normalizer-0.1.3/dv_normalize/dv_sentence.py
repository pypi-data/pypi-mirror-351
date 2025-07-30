import re
from typing import List, Optional
from dataclasses import dataclass
from dv_normalize.dv_numbers import DhivehiNumberConverter
from dv_normalize.dv_time import DhivehiTimeConverter
from dv_normalize.dv_years import DhivehiYearConverter

@dataclass
class DhivehiSentence:
    """Data class to store a Dhivehi sentence with its processed version."""
    raw: str
    processed: str
    length: int


class DhivehiTextProcessor:
    """A class to process Dhivehi text with cleaning and normalization."""
    
    def __init__(self, min_length: int = 15, max_length: int = 200, min_words: int = 3):
        """Initialize the text processor with length constraints."""
        self.min_length = min_length
        self.max_length = max_length
        self.min_words = min_words
        
        # Initialize mappings directly within the class
        self._initialize_mappings()
        
    def _initialize_mappings(self):
        """Initialize the character mappings directly in the code."""
        self.suffix_mappings = [
            {"suffix": "ހާއި", "spoken_as": "ހާ"},
            {"suffix": "ށާއި", "spoken_as": "ށާ"},
            {"suffix": "ނާއި", "spoken_as": "ނާ"},
            {"suffix": "ރާއި", "spoken_as": "ރާ"},
            {"suffix": "ބާއި", "spoken_as": "ބާ"},
            {"suffix": "ޅާއި", "spoken_as": "ޅާ"},
            {"suffix": "ކާއި", "spoken_as": "ކާ"},
            {"suffix": "އާއި", "spoken_as": "އާ"},
            {"suffix": "ވާއި", "spoken_as": "ވާ"},
            {"suffix": "މާއި", "spoken_as": "މާ"},
            {"suffix": "ފާއި", "spoken_as": "ފާ"},
            {"suffix": "ދާއި", "spoken_as": "ދާ"},
            {"suffix": "ތާއި", "spoken_as": "ތާ"},
            {"suffix": "ލާއި", "spoken_as": "ލާ"},
            {"suffix": "ގާއި", "spoken_as": "ގާ"},
            {"suffix": "ޏާއި", "spoken_as": "ޏާ"},
            {"suffix": "ސާއި", "spoken_as": "ސާ"},
            {"suffix": "ޑާއި", "spoken_as": "ޑާ"},
            {"suffix": "ޒާއި", "spoken_as": "ޒާ"},
            {"suffix": "ޓާއި", "spoken_as": "ޓާ"},
            {"suffix": "ޔާއި", "spoken_as": "ޔާ"},
            {"suffix": "ޕާއި", "spoken_as": "ޕާ"},
            {"suffix": "ޖާއި", "spoken_as": "ޖާ"},
            {"suffix": "ޗާއި", "spoken_as": "ޗާ"},
            {"suffix": "ޑރ", "spoken_as": "ޑޮކްޓަރު"},
            {"suffix": "ޑރ.", "spoken_as": "ޑޮކްޓަރު"},
            {"suffix": "ރޓޑ", "spoken_as": "ރިޑަޔަރޑް"}
        ]
        
        # Sentence ending mappings (previously eve_mappings)
        self.ending_mappings = [
            {"ending": "ހެކެވެ", "spoken_as": "ހެއް"},
            {"ending": "ރެއެވެ", "spoken_as": "ރޭ"},
            {"ending": "ލޮއެވެ", "spoken_as": "ލޮ"},
            {"ending": "ޓައެވެ", "spoken_as": "ޓާ"},
            {"ending": "ތީއެވެ", "spoken_as": "ތީ"},
            {"ending": "ލުމެވެ", "spoken_as": "ލުން"},
            {"ending": "ނެއެވެ", "spoken_as": "ނެ"},
            {"ending": "ކަށެވެ", "spoken_as": "ކަށް"},
            {"ending": "ނެެއެވެ", "spoken_as": "ނެ"},
            {"ending": "ބަބެވެ", "spoken_as": "ބު"},
            {"ending": "ވެއެވެ", "spoken_as": "ވޭ"},
            {"ending": "މެކެވެ", "spoken_as": "މެއް"},
            {"ending": "ފުޅެވެ", "spoken_as": "ފުޅު"},
            {"ending": "ގެއެވެ", "spoken_as": "ގެ"},
            {"ending": "ހުރެއެވެ", "spoken_as": "ހުރޭ"},
            {"ending": "ފައެވެ", "spoken_as": "ފައިވޭ"},
            {"ending": "ކެކެވެ", "spoken_as": "ކެއް"},
            {"ending": "ލެވެ", "spoken_as": "ލު"},
            {"ending": "ދެވެ", "spoken_as": "ދު"},
            {"ending": "ދެއެވެ", "spoken_as": "ދޭ"},
            {"ending": "ށަށެވެ", "spoken_as": "ށަށް"},
            {"ending": "ތުއެވެ", "spoken_as": "ތު"},
            {"ending": "ނޫނެވެ", "spoken_as": "ނޫން"},
            {"ending": "ންނެވެ", "spoken_as": "ން"},
            {"ending": "ތަށެވެ", "spoken_as": "ތަށް"},
            {"ending": "ދުނެވެ", "spoken_as": "ދުން"},
            {"ending": "ތަނެވެ", "spoken_as": "ތަން"},
            {"ending": "ރެކެވެ", "spoken_as": "ރެއް"},
            {"ending": "ބެއެވެ", "spoken_as": "ބޭ"},
            {"ending": "މެއެވެ", "spoken_as": "މޭ"},
            {"ending": "ޅައެވެ", "spoken_as": "ޅަ"},
            {"ending": "ކެވެ", "spoken_as": "އް"},
            {"ending": "މައެވެ", "spoken_as": "މަ"},
            {"ending": "ޔަށެވެ", "spoken_as": "ޔަށް"},
            {"ending": "ދުމެވެ", "spoken_as": "ދުން"},
            {"ending": "ށެކެވެ", "spoken_as": "ށެއް"},
            {"ending": "ވިއެވެ", "spoken_as": "ވި"},
            {"ending": "ރެވެ", "spoken_as": "ރު"},
            {"ending": "ޓަށެވެ", "spoken_as": "ޓަށް"},
            {"ending": "ޖެއެވެ", "spoken_as": "ޖެ"},
            {"ending": "ރުމެވެ", "spoken_as": "ރުން"},
            {"ending": "އްބެވެ", "spoken_as": "ވި"},
            {"ending": "ޅެވެ", "spoken_as": "ޅު"},
            {"ending": "އިންނެވެ", "spoken_as": "އިން"},
            {"ending": "ގަތެވެ", "spoken_as": "ގަތް"},
            {"ending": "އެކެވެ", "spoken_as": "އެއް"},
            {"ending": "އައެވެ", "spoken_as": "އައޭ"},
            {"ending": "ޅެކެވެ", "spoken_as": "ޅެއް"},
            {"ending": "ގައެވެ", "spoken_as": "ގައި"},
            {"ending": "ތެކެވެ", "spoken_as": "ތެއް"},
            {"ending": "ޔުމެވެ", "spoken_as": "ޔުން"},
            {"ending": "ބަހެވެ", "spoken_as": "ބަސް"},
            {"ending": "ވައެވެ", "spoken_as": "ވައި"}, # Patch, wind and vai, blimey
            {"ending": "އަށެވެ", "spoken_as": "އަށް"},
            {"ending": "ވީއެވެ", "spoken_as": "ވީ"},
            {"ending": "ފާތެވެ", "spoken_as": "ފާތު"},
            {"ending": "ބަހެކެވެ", "spoken_as": "ބަސް"},
            {"ending": "ކައެވެ", "spoken_as": "ކައި"},
            {"ending": "ގާމެވެ", "spoken_as": "ގާމު"},
            {"ending": "ހުއްޓެވެ", "spoken_as": "ހުރި"},
            {"ending": "ތަކެވެ", "spoken_as": "ތައް"},
            {"ending": "ޅެމެވެ", "spoken_as": "ޅެން"},
            {"ending": "ގަތުމެވެ", "spoken_as": "ގަތުން"},
            {"ending": "ވާތެވެ", "spoken_as": "ވާ"},
            {"ending": "މަށެވެ", "spoken_as": "މަށް"},
            {"ending": "މަށެެވެ", "spoken_as": "މަށް"},
            {"ending": "މަަށެވެ", "spoken_as": "މަށް"}, 
            {"ending": "ނެތެވެ", "spoken_as": "ނެތް"},
            {"ending": "ވަތެވެ", "spoken_as": "ވާ"},
            {"ending": "މަހެވެ", "spoken_as": "މަސް"},
            {"ending": "ވާށެވެ", "spoken_as": "ވޭ"},
            {"ending": "ރާށެވެ", "spoken_as": "ރޭ"},
            {"ending": "ހުމެވެ", "spoken_as": "ހުން"},
            {"ending": "ގާށެވެ", "spoken_as": "ގާ"},
            {"ending": "ބަޔެވެ", "spoken_as": "ބައި"},
            {"ending": "ލާހެވެ", "spoken_as": "ލާހު"},
            {"ending": "ރަމެވެ", "spoken_as": "ރަން"},
            {"ending": "ނީމެވެ", "spoken_as": "ނިން"},
            {"ending": "ގުނެވެ", "spoken_as": "ގުނެ"},
            {"ending": "ތީމެވެ", "spoken_as": "ތިން"},
            {"ending": "ނުނެވެ", "spoken_as": "ނުން"},
            {"ending": "ނުވެއެވެ", "spoken_as": "ނުވޭ"}, 
            {"ending": "ހީމެވެ", "spoken_as": "ހިން"},
            {"ending": "ދިނެވެ", "spoken_as": "ދިން"},
            {"ending": "ދާށެވެ", "spoken_as": "ދޭ"},
            {"ending": "ހަށެވެ", "spoken_as": "ހަށް"},
            {"ending": "ސެވެ", "spoken_as": "ސް"}, 
            {"ending": "ންޏެވެ", "spoken_as": "ނިން"},
            {"ending": "ކީމެވެ", "spoken_as": "ކޭ"},
            {"ending": "ދަމެވެ", "spoken_as": "ދަން"},
            {"ending": "ދައެވެ", "spoken_as": "ދާ"},
            {"ending": "ރީމެވެ", "spoken_as": "ރަން"},
            {"ending": "ނާށެވެ", "spoken_as": "ނާށޭ"},
            {"ending": "ރަށެވެ", "spoken_as": "ރަށް"},
            {"ending": "ކޮށެވެ", "spoken_as": "ކޮށް"},
            {"ending": "ހާށެވެ", "spoken_as": "ހަން"},
            {"ending": "ޅޭށެވެ", "spoken_as": "ޅެން"},
            {"ending": "ތުމެވެ", "spoken_as": "ތުން"},
            {"ending": "ޗަށެވެ", "spoken_as": "ޗަށް"},
            {"ending": "މިނެވެ", "spoken_as": "މިން"},
            {"ending": "ލަށެވެ", "spoken_as": "ލަށް"},
            {"ending": "ތޯއެވެ", "spoken_as": "ތޯ"},
            {"ending": "ވުމެވެ", "spoken_as": "ވުން"},
            {"ending": "ގޮތެވެ", "spoken_as": "ގޮތް"},
            {"ending": "ދޭށެވެ", "spoken_as": "ދޭށޭ"},
            {"ending": "ހެއްޔެވެ", "spoken_as": "ހެއްޔޭ"},
            {"ending": "ކާށެވެ", "spoken_as": "ކާށޭ"},
            {"ending": "ލާށެވެ", "spoken_as": "ލާށޭ"},
            {"ending": "އޮތެވެ", "spoken_as": "އޮތް"},
            {"ending": "ޤީނެވެ", "spoken_as": "ޤީނެު"},
            {"ending": "ނަމެވެ", "spoken_as": "ނަން"},
            {"ending": "ބޮޑެވެ", "spoken_as": "ބޮޑު"},
            {"ending": "ނަށެވެ", "spoken_as": "ނަށް"},
            {"ending": "ޓުނެވެ", "spoken_as": "ޓުނު"},
            {"ending": "ހެއެވެ", "spoken_as": "ހޭ"},
            {"ending": "ވުނެވެ", "spoken_as": "ވުނު"},
            {"ending": "ޅުމެވެ", "spoken_as": "ޅުން"},
            {"ending": "ޅަށެވެ", "spoken_as": "ޅަށް"},
            {"ending": "ލައެވެ", "spoken_as": "ލާ"},
            {"ending": "ކަމެވެ", "spoken_as": " "},
            {"ending": "އެވެ", "spoken_as": " "},
            {"ending": " އެވެ", "spoken_as": " "}

        ]
    
    def set_suffix_mappings(self, line: str) -> str:
        """Apply suffix mappings to the given line."""
        words = line.split()
        new_words = []
        
        for word in words:
            mapped_word = word
            for mapping in self.suffix_mappings:
                if word.endswith(mapping["suffix"]):
                    mapped_word = word.replace(mapping["suffix"], mapping["spoken_as"])
                    break
            new_words.append(mapped_word)
        
        return " ".join(new_words)
    
    def set_ending_mappings(self, line: str) -> str:
        """Apply sentence ending mappings to the given line."""
        if not line:
            return line
            
        words = line.split()
        if not words:
            return line
            
        last_word = words[-1]
        
        for mapping in self.ending_mappings:
            if last_word.endswith(mapping["ending"]):
                new_last_word = last_word.replace(mapping["ending"], mapping["spoken_as"])
                return " ".join(words[:-1] + [new_last_word])
        
        return line
    
    def check_bare_consonant_ending(self, line: str) -> bool:
        """Check if the line ends with a consonant with no diacritics."""
        if not line:
            return False
        
        words = [w for w in line.split() if w]
        if not words:
            return False

        last_word = words[-1]
        # Check from right to left if the last character is a consonant with no diacritics after it
        found_consonant = False
        
        for i in range(len(last_word) - 1, -1, -1):
            c = last_word[i]
            code_point = ord(c)
            
            # Check if it's a diacritic (0x07A6-0x07B0)
            if 0x07A6 <= code_point <= 0x07B0:
                # If we already found a consonant, then this diacritic is attached to it
                if found_consonant:
                    return False
                continue
            
            # If it's not a diacritic, it's a consonant (in Dhivehi script)
            # We found our first consonant from the right
            found_consonant = True
        
        # If we found a consonant and didn't return False, it means
        # the last consonant has no diacritics after it
        return found_consonant
    
    def break_to_lines(self, text: str) -> list:
        """Break text into lines at sentence endings but preserve decimal numbers."""
        # First remove all new lines
        text = re.sub(r'\n', ' ', text)

        # Next replace all double spaces with single spaces
        text = re.sub(r'\s+', ' ', text)

        # Replace decimal numbers with placeholders
        decimal_pattern = r'\b\d+\.\d+\b'
        nums = re.findall(decimal_pattern, text)
        temp_text = text
        for i, num in enumerate(nums):
            temp_text = temp_text.replace(num, f"__NUM_{i}__")
        # Split by periods and exclamation marks
        lines = []
        current_line = []
        for p in temp_text.split("."):
            p = p.strip()
            if p:
                for q in p.split("!"):
                    q = q.strip()
                    if q:
                        words = q.split()
                        if len(words) >= 4:
                            last_word = words[-1]
                            # Check if the last word has an opening punctuation
                            if any(c in last_word for c in '"\''):
                                # If it has opening punctuation, add to current line
                                current_line.extend(words)
                            else:
                                # If current line exists, add it to lines
                                if current_line:
                                    lines.append(" ".join(current_line))
                                    current_line = []
                                # Check if the last word is valid
                                last_word = last_word.rstrip('"\'")')
                                #if len(last_word) >= 4 and not any(c in last_word for c in '[]{}<>@#$%^&*+=|\\/~`'):
                                lines.append(q)
        
        # Add any remaining current line if it exists
        if current_line:
            lines.append(" ".join(current_line))
            
        # Restore decimal numbers
        for i, line in enumerate(lines):
            for j, num in enumerate(nums):
                lines[i] = line.replace(f"__NUM_{j}__", num)
        return lines
    
    def clean_sentence(self, text: str, keep_english: bool = False, remove_punctuation: bool = True, remove_arabic: bool = True) -> str:
        """Remove emojis, English text, and Arabic characters from input."""
        if not text:
            return text

        # 1. Remove emojis and special symbols
        emoji_pattern = re.compile(
            "["
            "\U0001F000-\U0001F9FF"  # Extended pictographic
            "\U0001F300-\U0001F5FF"  # Miscellaneous Symbols and Pictographs
            "\U0001F600-\U0001F64F"  # Emoticons
            "\U0001F680-\U0001F6FF"  # Transport and Map
            "\U0001F700-\U0001F77F"  # Alchemical Symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U00002600-\U000027BF"  # Miscellaneous Symbols
            "\U0000FE00-\U0000FE0F"  # Variation Selectors
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251" 
            "\U00002700-\U000027BF"
            "\u2764\uFE0F"  # Heavy Black Heart (with variation selector)
            "\u2764"        # Heavy Black Heart (without variation selector)
            "❤"            # Direct heart character
            "]",
            flags=re.UNICODE
        )
        text = emoji_pattern.sub(r'', text)

        # 2. Remove HTML entities
        text = re.sub(r'&#x[0-9a-fA-F]+;|&#[0-9]+;', '', text)

        # 3. Remove English text if not keeping it
        if not keep_english:
            text = re.sub(r'[a-zA-Z]+', '', text)

        # 4. Remove punctuation if specified
        if remove_punctuation:
            text = re.sub(r'["\']', '', text)

        # 5. Remove Arabic characters except ﷺ and ﷲ
        if remove_arabic:
            text = re.sub(r'[؀-ۿ](?<!ﷺ)(?<!ﷲ)', '', text)

        # 6. Remove special characters and symbols (after Arabic handling)
        special_chars = [
            '©®™℠§¶†‡•♦♥♠♣★☆♪♫♯',  # Special symbols
            '[](){}<>',              # All types of brackets
            '/\\_#|',                # Other special characters
            '،؛؟',                   # Arabic punctuation
            '،',                     # Arabic comma
            '؛',                     # Arabic semicolon
            '؟'                      # Arabic question mark
            '-',
            '—'
        ]
        # Create pattern that excludes ﷺ and ﷲ
        special_chars_pattern = f'[{re.escape("".join(special_chars))}]'
        text = re.sub(special_chars_pattern, '', text)

        # 7. Remove control characters and zero-width spaces
        control_chars_pattern = re.compile(
            r'['
            '\u0000-\u001F'  # C0 controls
            '\u007F-\u009F'  # C1 controls
            '\u200B-\u200F'  # Zero-width chars and direction marks
            '\u2028-\u202E'  # Line/paragraph separators and direction overrides
            '\u2066-\u2069'  # Bidirectional isolate controls
            '\uFEFF'         # Byte Order Mark
            '\uFFF9-\uFFFC'  # Interlinear annotations
            ']',
            flags=re.UNICODE
        )
        text = control_chars_pattern.sub('', text)

        # 8. Clean up spaces
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        return text
    
    def format_dhivehi_single_consonant(self, sentence: str) -> str:
        """Format Dhivehi single consonant with a period."""
        # Pattern to match single or double Dhivehi letter abbreviations followed by a space and a word
        # The pattern uses a word boundary \b to ensure we match whole abbreviations
        pattern = r'\b([ހށނރބޅކއވމފދތލގޏސޑޖޗޒޓޔޕޤޥ]|[ހށނރބޅކއވމފދތލގޏސޑޖޗޒޓޔޕޤޥ][ހށނރބޅކއވމފދތލގޏސޑޖޗޒޓޔޕޤޥ]) ([^\s]+)'
        
        # Replace with the same matches but add a period between them
        formatted_text = re.sub(pattern, r'\1.\2', sentence)
        
        return formatted_text
    
    def replace_dhivehi_consonant_with_full_word(self, sentence: str) -> str:
        """Replace Dhivehi consonant with its full word."""
        letter_map = {
            'ހ': 'ހާ',
            'ށ': 'ށަވިޔަނި',
            'ނ': 'ނޫނު',
            'ރ': 'ރާ', 
            'ބ': 'ބާ',
            'ޅ': 'ޅަވިޔަނި',
            'ކ': 'ކާފު',
            'އ': 'އަލިފު',
            'ވ': 'ވާވު',
            'މ': 'މީމު',
            'ފ': 'ފާފު',
            'ދ': 'ދާލު',
            'ތ': 'ތާ',
            'ލ': 'ލާމު',
            'ގ': 'ގާފު',
            'ޏ': 'ޏަވިޔަނި',
            'ސ': 'ސީނު',
            'ޑ': 'ޑަވިޔަނި',
            'ޒ': 'ޒަވިޔަނި',
            'ޓ': 'ޓަވިޔަނި',
            'ޔ': 'ޔާ',
            'ޕ': 'ޕަވިޔަނި',
            'ޖ': 'ޖަވިޔަނި',
            'ޗ': 'ޗަވިޔަނި',
            'ޘ': 'ޘާ',
            'ޙ': 'ޙާ',
            'ޚ': 'ޚާ',
            'ޛ': 'ޛާލު',
            'ޜ': 'ޜާ',
            'ޝ': 'ޝީނު',
            'ޞ': 'ޞާދު',
            'ޟ': 'ޟާދު',
            'ޠ': 'ޠޯ',
            'ޡ': 'ޡޯ',
            'ޢ': 'ޢައިނު',
            'ޣ': 'ޣައިނު',
            'ޤ': 'ޤާފު',
            'ޥ': 'ޥާވު'
        }

        def replace_with_full_form(match):
            abbr = match.group(1)
            following_word = match.group(2)
            
            # Get the previous word
            prev_word_match = re.search(r'\S+\s+$', sentence[:match.start()])
            prev_word = prev_word_match.group(0).strip() if prev_word_match else ''
            
            # Check if previous word contains numbers and current abbreviation is ރ
            if abbr == 'ރ' and re.search(r'\d', prev_word):
                return f"ރުފިޔާ {following_word}"
            
            # If the abbreviation exists in our map, replace it
            if abbr in letter_map:
                return f"{letter_map[abbr]} {following_word}"
            else:
                # If not in our map, just add the period
                return f"{abbr} {following_word}"
    
        # Pattern to match single or double Dhivehi letter abbreviations followed by a space and a word
        pattern = r'\b([ހށނރބޅކއވމފދތލގޏސޑޖޗޒޓޔޕޤޥ]|[ހށނރބޅކއވމފދތލގޏސޑޖޗޒޓޔޕޤޥ][ހށނރބޅކއވމފދތލގޏސޑޖޗޒޓޔޕޤޥ]) ([^\s]+)'
        
        # Replace abbreviations with their full forms
        formatted_text = re.sub(pattern, replace_with_full_form, sentence)
        
        return formatted_text

    def parse_dhivehi_to_numbers(self, text:str)->str:
        """Parse Dhivehi text to detect and convert numbers, times, and years to their written form."""

        # Step 1: Add spaces around numbers to separate them from surrounding text
        # Define a pattern for numbers with various separators (commas, periods, hyphens, colons)
        # This pattern matches numbers like: 44,000 44-223 44:40 44.50

        # First, define what a number can look like (including internal separators)
        num_pattern = r'\d+(?:[.,،\-:/]\d+)*'

        # Handle numbers adjacent to text (on both sides)
        text = re.sub(f'([^\d.,،\-:/])({num_pattern})([^\d.,،\-:/])', r'\1 \2 \3', text)

        # Handle numbers at the beginning of text followed by non-number chars
        text = re.sub(f'^({num_pattern})([^\d.,،\-:/])', r'\1 \2', text)

        # Handle numbers at the end of text preceded by non-number chars
        text = re.sub(f'([^\d.,،\-:/])({num_pattern})$', r'\1 \2', text)

        # Special case for when the number has a suffix directly attached
        # This handles cases like "44,000އަށްވުރެ"
        text = re.sub(f'({num_pattern})([^\s\d.,،\-:/])', r'\1 \2', text)

        # Special case for when the number has a suffix directly attached
        # Replace cases like: 2000ރ. → 2000 ރުފިޔާ, 2000 ރ. → 2000 ރުފިޔާ, 2000 ރ → 2000 ރުފިޔާ
        text = re.sub(r'(\d+(?:[.,]\d+)?)(\s?)(ރ)\.?', r'\1 ރުފިޔާ', text)

        print(text)


        # Store all matches with their positions to handle replacements properly
        replacements = []

        # Pattern for years (4 digits that could be a year)
        year_pattern = r'\b(1\d{3}|20\d{2})\b'

        # Pattern for time in format HH:MM
        time_pattern = r'\b(?:(?:[0-9]|0[0-9]|1[0-9]|2[0-3]):(?:[0-5][0-9]))\b'

        # Pattern for numbers - handle both Latin and Arabic/Dhivehi separators
        # The pattern now includes both , and ، as possible thousand separators
        number_pattern = r'\b(\d{1,3}([,،]\d{3})*|\d+)(\.\d+)?\b'

        # Find years
        for match in re.finditer(year_pattern, text):
            year = match.group(0)
            start, end = match.span()
            year_written = DhivehiYearConverter.convert(int(year))
            replacements.append((start, end, year_written))

        # Find times
        for match in re.finditer(time_pattern, text):
            time_str = match.group(0)
            start, end = match.span()
            
            # Validate the time format (extra safety)
            hour, minute = map(int, time_str.split(':'))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                time_written = DhivehiTimeConverter.convert(time_str)
                replacements.append((start, end, time_written))

        # Find numbers
        for match in re.finditer(number_pattern, text):
            number_str = match.group(0)
            start, end = match.span()

            # Skip if the position overlaps with a year or time already identified
            skip = False
            for r_start, r_end, r_replacement in replacements:
                if (start >= r_start and start < r_end) or (end > r_start and end <= r_end):
                    skip = True
                    break

            if not skip:
                # Check if this is a number with a decimal point
                if '.' in number_str:
                    # Clean number by removing both types of separators
                    clean_number = number_str.replace(',', '').replace('،', '')

                    # Split into integer and decimal parts
                    integer_part, decimal_part = clean_number.split('.')

                    # Handle empty parts (like ".5" or "5.")
                    if integer_part == '':
                        integer_written = DhivehiNumberConverter.convert(0)
                    else:
                        integer_written = DhivehiNumberConverter.convert(int(integer_part))

                    if decimal_part == '':
                        decimal_written = DhivehiNumberConverter.convert(0)
                    else:
                        decimal_written = DhivehiNumberConverter.convert(int(decimal_part))

                    # Add the "ޕޮއިންޓް" (point) between integer and decimal parts
                    number_written = f"{integer_written} ޕޮއިންޓް {decimal_written}"
                else:
                    # For regular numbers without decimal points
                    clean_number = number_str.replace(',', '').replace('،', '')
                    number_written = DhivehiNumberConverter.convert(int(clean_number))

                replacements.append((start, end, number_written))

        # Sort by position in reverse order to avoid affecting other replacements
        replacements.sort(key=lambda x: x[0], reverse=True)

        # Apply all replacements
        result = text
        for start, end, replacement_text in replacements:
            result = result[:start] + replacement_text + result[end:]

        return result
    
    def process_sentence(self, sentence: str,consonant_full_word:bool=True, apply_dv_numbers:bool=True) -> Optional[DhivehiSentence]:
        """Process a single sentence with selected normalization."""
        if not sentence:
            return None
        # Preprocess the sentence
        sentence = sentence.strip()
        words = sentence.split()
        
        if (len(sentence) < self.min_length or 
            len(sentence) > self.max_length or 
            len(words) < self.min_words):
            return None
            
        # Apply normalization
        processed = sentence
        processed = self.clean_sentence(processed)
        processed = self.set_suffix_mappings(processed)
        processed = self.set_ending_mappings(processed)

        # Apply correct consonant normalization
        if consonant_full_word:
            processed = self.replace_dhivehi_consonant_with_full_word(processed)
        else :
            processed = self.format_dhivehi_single_consonant(processed)

        # Apply Dhivehi numbers
        if apply_dv_numbers:
            processed = self.parse_dhivehi_to_numbers(processed)

        # Remove double or multiple spaces
        sentence = re.sub(r'\s+', ' ', sentence).strip()
        processed = re.sub(r'\s+', ' ', processed).strip()

        # Prepare the result
        if processed and len(processed.strip()) >= self.min_length:
            return DhivehiSentence(
                raw=sentence,
                processed=processed,
                length=len(processed)
            )
            
        return None
    
    def process_text(self, text: str,consonant_full_word:bool=True, apply_dv_numbers:bool=True) -> List[DhivehiSentence]:
        """Process the entire text and return a list of processed sentences."""
        # Break to lines
        lines = self.break_to_lines(text)
        
        # Process each line
        results = []
        next_line = ""
        
        for line in lines:
            line = line.strip()

            # Combine with next line if exists
            if next_line:
                line = next_line + " " + line

            # If this line ends with a bare consonant, buffer it and continue
            if self.check_bare_consonant_ending(line):
                next_line = line
                continue
            else:
                next_line = ""  # Clean up
            
            # Seperate words
            words = line.split()
            current_chunk = []
            current_length = 0
            
            for word in words:
                if current_length + len(word) + len(current_chunk) > self.max_length and current_chunk:
                    chunk_text = " ".join(current_chunk)
                    
                    # Send to process in chunks
                    result = self.process_sentence(chunk_text,consonant_full_word, apply_dv_numbers)                    

                    if result:
                        results.append(result)
                    
                    # Initialize new chunk
                    current_chunk = [word]
                    current_length = len(word)
                else:
                    current_chunk.append(word)
                    current_length += len(word)
            
            # Send the last chunk if it exists
            if current_chunk:
                chunk_text = " ".join(current_chunk)
                result = self.process_sentence(chunk_text,consonant_full_word, apply_dv_numbers)
                if result:
                    results.append(result)
        
        # Send any pending as next line
        if next_line:
            result = self.process_sentence(next_line,consonant_full_word, apply_dv_numbers)
            if result:
                results.append(result)
        
        return results

    def process_full_text(self, text: str,consonant_full_word:bool=True, apply_dv_numbers:bool=True) -> str:
        """Process the entire text while preserving its structure."""
        if not text:
            return ""
            
        # Process the text using the existing method
        processed_sentences = self.process_text(text,consonant_full_word, apply_dv_numbers)
        
        # Combine the processed sentences
        return "، ".join(sentence.processed for sentence in processed_sentences)

    def process_full_text_preserve_line_breaks(self, text: str, consonant_full_word: bool = True, apply_dv_numbers: bool = True) -> str:
        """Process the entire text while preserving its line breaks."""
        if not text:
            return ""
        
        # Split by original newlines
        original_lines = text.split('\n')
        processed_output = []
        
        for line in original_lines:
            line = line.strip()
            if not line:
                processed_output.append("")  # Preserve blank lines
                continue
            
            # Process each line individually
            processed_sentences = self.process_text(line, consonant_full_word, apply_dv_numbers)
            
            # Combine processed sentences from this line
            combined_line = "، ".join(sentence.processed for sentence in processed_sentences)
            processed_output.append(combined_line)
        
        # Join back with original line breaks
        return "\n".join(processed_output)

    # Old Aliases
    def spoken_dv(self,text:str, preserve_line_breaks:bool=True)->str:
        """Alias for process_full_text"""
        if preserve_line_breaks:
            return self.process_full_text_preserve_line_breaks(text)
        else:
            return self.process_full_text(text)
    
    def int_to_dv(self,text:str)->str:
        """Alias for process_full_text"""
        return self.parse_dhivehi_to_numbers(text)
    