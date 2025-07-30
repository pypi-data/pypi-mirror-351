# GeoAddressCleaner

A lightweight Python package for cleaning and standardizing US street addresses before geocoding or mapping.  
It focuses on parsing, formatting, and basic validation of address strings.

---

## Features

- **Parses US addresses** from various formats (with or without commas)
- **Standardizes addresses** to a consistent format:  
  `Street, City, State ZIP`
- **Validates state abbreviations** and basic address structure
- **Optional geocoding** (requires `geopy`)

---

## Installation

Install the package using pip:pip install geoaddresscleaner



Or, for development, install in editable mode from the project root:pip install -e .


---

## Usage

from geoaddresscleaner.core import standardize_address, validate_address
Standardize an address

print(standardize_address("123 main st, springfield, il 62704"))
Output: "123 Main St, Springfield, IL 62704"
Validate an address

print(validate_address("123 main st, springfield, il 62704"))
Output: True


---

## Contributing

Contributions are welcome!  
Please open an issue or submit a pull request on GitHub.

---

## License

[MIT License](LICENSE)




