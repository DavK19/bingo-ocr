# Bingo OCR Project

## Overview
This project is designed to read and process images of bingo cards using Optical Character Recognition (OCR). It divides the bingo card into a 5x5 grid, processes each cell, and extracts the numbers using Tesseract OCR.

## Project Structure
```
bingo-ocr
├── src
│   ├── main.py          # Entry point for the application
│   ├── processor.py     # Handles image processing and grid division
│   ├── ocr.py           # Contains OCR-related functions
│   ├── preproc.py       # Preprocessing functions for image enhancement
│   └── utils.py         # Utility functions for various tasks
├── tests
│   └── test_processor.py # Unit tests for processor functions
├── requirements.txt      # Project dependencies
├── .gitignore            # Files and directories to ignore in Git
└── README.md             # Project documentation
```

## Installation
To set up the project, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd bingo-ocr
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Ensure that Tesseract OCR is installed on your system. You can download it from [Tesseract's official repository](https://github.com/tesseract-ocr/tesseract).

## Usage
To run the application, execute the following command:
```
python src/main.py <path_to_bingo_card_image>
```
Replace `<path_to_bingo_card_image>` with the path to your bingo card image file.

## Testing
To run the unit tests, navigate to the `tests` directory and execute:
```
pytest test_processor.py
```

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.