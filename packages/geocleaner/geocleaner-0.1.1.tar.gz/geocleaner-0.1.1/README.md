# GeoCleaner

A lightweight Python package for cleaning and standardizing US street addresses before geocoding or mapping.  
It focuses on basic capitalization of place name strings.

---

## Features

-Capitalizes Place Names to capitalize first letter of each word
---

## Installation

Install the package using pip:pip install geocleaner



Or, for development, install in editable mode from the project root:pip install -e .


---

## Usage

from geocleaner.core import clean_location
print(clean_location("   new york  "))   # → "New York"


---

## Contributing

Contributions are welcome!  
Please open an issue or submit a pull request on GitHub.

---

## License

[MIT License](LICENSE) 
