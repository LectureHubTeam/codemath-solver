# CodeMath Solver

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A robust tool for scraping, processing, and solving coding/math problems using AI-driven automation.

---

## 🚀 Features
- **Problem Crawling**: Automatically scrape problems from online platforms using Selenium-based crawlers
- **PDF Processing**: Extract questions and metadata from PDF documents
- **AI-Powered Solutions**: Leverage Google's Generative AI to generate code/math solutions
- **Smart Problem Selection**: Filter and curate problems based on difficulty/subject using ML algorithms
- **End-to-End Workflow**: From data ingestion to solution generation in a single CLI interface

---

## 📦 Installation
```bash
# Clone repository
git clone https://github.com/your-username/codemath-solver.git
cd codemath-solver

# Install dependencies
pip install -r requirements.txt

# Configure settings
cp conf/settings.example.py conf/settings.py  # Create config file
```

---

## 🏃♂️ Usage
```bash
# Run full workflow
python app.py --crawl --process --solve

# Individual components
python app.py crawl --source=leetcode
python app.py process --input=data/raw_problems.pdf
python app.py solve --problem-id=123
```

---

## 📂 Folder Structure
```
codemath-solver/
├── app.py               # Main CLI entrypoint
├── codemath_solver/     # Core modules
│   ├── agent/           # AI interaction components
│   │   └── llm.py      # Large Language Model interface
│   ├── crawl/           # Web scraping modules
│   │   └── core.py     # Crawling engine
│   └── utils/           # Utility functions
│       ├── process_pdf.py
│       └── select_problems.py
├── conf/                # Configuration files
├── data/                # Input/output data storage
└── tests/               # Test suites
```

---

## 🤝 Contributing
1. Fork the repository
2. Create feature branch: `git checkout -b feature/YourFeature`
3. Implement changes with tests
4. Lint code with `pre-commit run --all-files`
5. Submit PR with clear description

---

## 📖 Documentation
### Configuration Options
Edit `conf/settings.py` to customize:
```python
# Example configuration
CRAWL_SOURCES = ["leetcode", "codeforces"]
MAX_PROBLEMS = 50
SOLUTION_TIMEOUT = 30  # seconds
```

---

## 📌 License
Released under the [MIT License](LICENSE). Feel free to modify and distribute.

---

Made with ❤️ using Python and AI technologies
