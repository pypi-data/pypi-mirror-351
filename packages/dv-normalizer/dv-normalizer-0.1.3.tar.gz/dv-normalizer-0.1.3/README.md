# dv-normalize

A Python library for normalizing Dhivehi text by converting numbers to Dhivehi and standardizing sentence endings.

## Features

- Converts numbers to Dhivehi text (both written and spoken forms)
- Handles years
- Handles decimal numbers
- Normalizes formal sentence endings to colloquial form
- Preserves proper spacing and punctuation
- Converts time to Dhivehi format
- Processes full text with mixed content (numbers, years, times, and sentences)

## Installation

```bash
pip install dv-normalize
```

## Usage

The library provides several main components for different types of conversions:

### 1. Number Conversion

```python
from dv_normalize.dv_numbers import DhivehiNumberConverter

# Basic number conversion
result = DhivehiNumberConverter.convert(232)

# Large numbers
result = DhivehiNumberConverter.convert(7878787874151545121545454)

# Negative numbers
result = DhivehiNumberConverter.convert(-21)
```

### 2. Time Conversion

```python
from dv_normalize.dv_time import DhivehiTimeConverter

# Convert time to Dhivehi
result = DhivehiTimeConverter.convert("14:30")
result = DhivehiTimeConverter.convert("01:30")
result = DhivehiTimeConverter.convert("00:00")
```

### 3. Year Conversion

```python
from dv_normalize.dv_years import DhivehiYearConverter

# Convert years to Dhivehi
result = DhivehiYearConverter.convert(1960)
result = DhivehiYearConverter.convert(2023)
```

### 4. Text Processing

```python
from dv_normalize.dv_sentence import DhivehiTextProcessor

# Create processor instance
processor = DhivehiTextProcessor()

# Process individual sentences
result = processor.spoken_dv("ވަކި ލާރިން ވެސް 232.23 ލާރި ހޯދައެވެ")

# Process full text with mixed content
sample_text = """
އިބްރާހިމް އަކީ 1982 އިން 2024 ވަނަ އަހަރާއި ހަމައަށް ވަޒީފާގައި އުޅުން މީހެކެވެ.
"""
result = processor.process_full_text(sample_text)

# Process text as separate sentences
sentence_results = processor.process_text(sample_text)
for result in sentence_results:
    print(f"Raw: {result.raw}")
    print(f"Processed: {result.processed}")
    print(f"Length: {result.length}")
```
## Test Cases

```python
""" Dhivehi Number Converter """
from dv_normalize.dv_numbers import DhivehiNumberConverter
# Test cases for numbers
if __name__ == "__main__":
    test_cases = [
        (0, "ސުމެއް"),
        (1, "އެކެއް"),
        (10, "ދިހައެއް"),
        (15, "ފަނަރަ"),
        (20, "ވިހި"),
        (21, "އެކާވީސް"),
        (22, "ބާވީސް"),
        (25, "ފަންސަވީސް"),
        (29, "ނަވާވީސް"),
        (30, "ތިރީސް"),
        (100, "އެއް ސަތޭކަ"),
        (101, "އެއް ސަތޭކަ އެކެއް"),
        (110, "އެއް ސަތޭކަ ދިހައެއް"),
        (115, "އެއް ސަތޭކަ ފަނަރަ"),
        (121, "އެއް ސަތޭކަ އެކާވީސް"),
        (1000, "އެއް ހާސް"),
        (1001, "އެއް ހާސް އެކެއް"),
        (1021, "އެއް ހާސް އެކާވީސް"),
        (8988, "އަށް ހާސް ނުވަ ސަތޭކަ އައްޑިހަ އަށެއް"),
        (100000, "އެއް ލައްކަ"),
        (200000, "ދެ ލައްކަ"),
        (955545102, "ނުވަ ސަތޭކަ ފަންސާސް ފަސް މިލިއަން ފަސް ލައްކަ ސާޅީސް ފަސް ހާސް އެއް ސަތޭކަ ދޭއް"),
        (7878787874151545121545454,"ހަތެއް އަށެއް ހަތެއް އަށެއް ހަތެއް އަށެއް ހަތެއް އަށެއް ހަތެއް ހަތަރެއް އެކެއް ފަހެއް އެކެއް ފަހެއް ހަތަރެއް ފަހެއް އެކެއް ދޭއް އެކެއް ފަހެއް ހަތަރެއް ފަހެއް ހަތަރެއް ފަހެއް ހަތަރެއް"),
        (-5, "މައިނަސް ފަހެއް"),
        (-21, "މައިނަސް އެކާވީސް")
    ]
    
    print("Testing Dhivehi number converter with known cases:")
    for number, expected in test_cases:
        result = DhivehiNumberConverter.convert(number)
        print(f"{number}: {result}")
        if result != expected:
            print(f"  Expected: '{expected}'")
            print(f"  Got: '{result}'")
    
""" Dhivehi Time Converter """
from dv_normalize.dv_time import DhivehiTimeConverter

# Test cases for times
if __name__ == "__main__":
    # Comprehensive test with various time formats
    print("Testing Dhivehi time converter (Comprehensive Test):")
    
    # First, test the existing cases
    existing_test_cases = [
        ("14:30", "ސާދަ ގަޑި ތިރީސް"),
        ("01:30", "އެއް ގަޑި ތިރީސް"),
        ("01:21", "އެއް ގަޑި އެކާވީސް"),
        ("00:00", "ބާރަ ގަޑި ސުމެއް"),  # Auto-detected as 12-hour format
        ("23:59", "ތޭވީސް ގަޑި ފަންސާސް ނުވައެއް"),
        ("12:00", "ބާރަ ގަޑި ސުމެއް"),
        ("00:01", "ބާރަ ގަޑި އެކެއް"),  # Auto-detected as 12-hour
        ("05:15", "ފަސް ގަޑި ފަނަރަ"),
        ("10:45", "ދިހަ ގަޑި ސާޅީސް ފަހެއް"),
        ("17:05", "ސަތާރަ ގަޑި ފަހެއް"),
        ("20:30", "ވިހި ގަޑި ތިރީސް"),
        ("18:25", "އަށާރަ ގަޑި ފަންސަވީސް"),
    ]
    
    print("\n=== Testing Original Cases ===")
    for time_str, expected in existing_test_cases:
        result = DhivehiTimeConverter.convert(time_str)
        print(f"{time_str}: {result}")
        if result != expected:
            print(f"  Expected: '{expected}'")
            print(f"  Got: '{result}'")
    
    # Test all hours with 00 minutes
    print("\n=== Testing All Hours with 00 Minutes ===")
    for hour in range(24):
        time_str = f"{hour:02d}:00"
        result = DhivehiTimeConverter.convert(time_str)
        print(f"{time_str}: {result}")
    
    # Test hour 12 with all minutes (covers standard hour)
    print("\n=== Testing Hour 12 with Various Minutes ===")
    for minute in range(0, 60, 5):  # Test every 5 minutes for brevity
        time_str = f"12:{minute:02d}"
        result = DhivehiTimeConverter.convert(time_str)
        print(f"{time_str}: {result}")
    
    # Test special minute values (covering all tens places)
    print("\n=== Testing Various Hours with Special Minute Values ===")
    special_minutes = [0, 1, 10, 11, 19, 20, 21, 25, 29, 30, 40, 50, 55, 59]
    for minute in special_minutes:
        # Test with different hours to cover both 12-hour and 24-hour formats
        for hour in [0, 1, 12, 23]:
            time_str = f"{hour:02d}:{minute:02d}"
            result = DhivehiTimeConverter.convert(time_str)
            print(f"{time_str}: {result}")
    
    # Test for invalid inputs
    print("\n=== Testing Invalid Inputs ===")
    invalid_inputs = ["24:00", "12:60", "abc", "12:xx", "24:60", "-1:30"]
    for invalid in invalid_inputs:
        result = DhivehiTimeConverter.convert(invalid)
        print(f"{invalid}: {result}")
    
    print("\nTime Testing completed!")

""" Dhivehi Year Converter """
from dv_normalize.dv_years import DhivehiYearConverter

# Test cases for years
if __name__ == "__main__":
    year_test_cases = [
        (1960, "ނަވާރަސަތޭކަ ފަސްދޮޅަސް"),
        (2000, "ދެހާސް"),
        (2023, "ދެހާސް ތޭވީސް"),
        (1492, "ސާދަސަތޭކަ ނުވަދިހަ ދޭއް"),
        (1985, "ނަވާރަސަތޭކަ އައްޑިހަ ފަސް"),
        (1800, "އަށާރަސަތޭކަ"),
        (1234, "ބާރަސަތޭކަ ތިރީސް ހަތަރު"),
        (2525, "ދެހާސް ފަސްސަތޭކަ ފަންސަވީސް"),
        (1066, "އެއްހާސް ފަސްދޮޅަސް ހަ"),
        (622, "ހަސަތޭކަ ބާވީސް"),
        (50, "ފަންސާސް"),
        (-44, "ސާޅީސް ހަތަރު ކުރީގެ"),
    ]
    
    print("Testing Dhivehi year converter:")
    for year, expected in year_test_cases:
        result = DhivehiYearConverter.convert(year)
        print(f"{year}: {result}")
        if result != expected:
            print(f"  Expected: '{expected}'")
            print(f"  Got: '{result}'")
    
""" Dhivehi Sentence Converter """
from dv_normalize.dv_sentence import DhivehiTextProcessor

# Test cases for sentences

"""Demo function to test the processor."""
# Sample Dhivehi text for testing
sample_text = """
އިބްރާހިމް އަކީ 1982 އިން 2024 ވަނަ އަހަރާއި ހަމައަށް ވަޒީފާގައި އުޅުން މީހެކެވެ. މިގޮތުން ކޮންމެ ދުވަހަކު ހެދުނު 08:00 އިން ފަށައިގެ ގޮސް ހަވީރު 16:00 އަށް އޮފީހުގައި އުޅުމަށް ފަހު ގެޔަށް ދިޔުމަށް ނުކުމެއެވެ. އަދި ހެލެމެޓް ގަދަކަމުން ބޮލަށް ފައްތާލައިގެން، ބާރު ސްޕީޑްގައި ގެޔަށް ނައްޓާލައެވެ. ބައެއް ފަހަރުގަ ކ.އަތޮޅު ވިލިނގިލިން ނައްޓައިލަގެން ގުޅީފަޅަށް 15 މިނެޓްތެރޭ ދާއިރު ސްޕީޑް ހުންނަނީ 120 ކިލޯ މީޓަރު ބާރު މިނުގައެވެ. މިސޮރު މިހެން އުޅެ ކޮންމެ މަހަކު 52،1092 ރުފިޔާ ގެޔަށް ގެންދެއެވެ. އިތުރު މަސައްކަތް ކޮށްގެން 9982711 ރ މިވަރަށް ހޯދާ ކަމަށް ވެއެވެ. ވަކި ލާރިން ވެސް 232.23 ލާރި ހޯދައެވެ
"""

# Create processor
processor = DhivehiTextProcessor()

# Process as sentences
print("Processing as sentences:")
print("-" * 50)
sentence_results = processor.process_text(sample_text)
print(f"Processed {len(sentence_results)} sentences:")
for idx, result in enumerate(sentence_results, 1):
    print(f"\nSentence {idx}:")
    print(f"Raw: {result.raw}")
    print(f"Processed: {result.processed}")
    print(f"Length: {result.length}")

# Process as full text
print("\nProcessing as full text:")
print("-" * 50)
full_text_result = processor.process_full_text(sample_text)
print("Processed full text:")
print(full_text_result)


# Seprate alias test
print("Testing alias functions:")
print("-" * 50)
print("Testing spoken_dv:")
print(processor.spoken_dv("ވަކި ލާރިން ވެސް 232.23 ލާރި ހޯދައެވެ"))
print(processor.spoken_dv("ވަކި ލާރިން ވެސް 232,23 ލާރި ހޯދައެވެ"))
print(processor.spoken_dv("މި މަހުގެ 11ވަނަ ދުވަހު ބާއްވަން ނިންމައިފި"))
print(processor.spoken_dv("ޣައްޒާގެ މުސްލިމުންނާ ދެކޮޅަށް މީގެ ތޭރަ މަސް ކުރިން ޔަހޫދީ ފައުޖުން ފެށި ލާއިންސާނީ ޢުދުވާނުގައި ޝަހީދު ކޮށްލާފައިވާ މީހުންގެ އަދަދު ވަނީ 20:00އަށްވުރެ މައްޗަށް އުފުލިފައިވޭ"))
print(processor.spoken_dv("މީގެ ކުރިން އެ މަގާމުގައި ހުންނެވީ ޖެނުއަރީ  ނުވައެއް  2024ގައި އެ މަގާމަށް އައްޔަނުކުރެއްވި އެ ކުންފުނީގެ މެނޭޖިން ޑިރެކްޓަރުކަން ވެސް ކުރައްވާފައިވާ މުހައްމަދު މިހާދު"))

print("Testing int_to_dv:")
print(processor.int_to_dv("232"))
print(processor.int_to_dv("7878787874151545121545454"))
```
## Example Outputs

### Numbers
- 0 → ސުމެއް
- 1 → އެކެއް
- 10 → ދިހައެއް
- 100 → އެއް ސަތޭކަ
- 1000 → އެއް ހާސް

### Time
- 14:30 → ސާދަ ގަޑި ތިރީސް
- 01:30 → އެއް ގަޑި ތިރީސް
- 00:00 → ބާރަ ގަޑި ސުމެއް

### Years
- 1960 → ނަވާރަސަތޭކަ ފަސްދޮޅަސް
- 2023 → ދެހާސް ތޭވީސް
- 1492 → ސާދަސަތޭކަ ނުވަދިހަ ދޭއް

## Known Issues

- Not all sentence endings are normalized.

## License

This project is licensed under the [MIT](https://opensource.org/licenses/MIT) License.