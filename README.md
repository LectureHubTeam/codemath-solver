# CodeMath Solver

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A robust tool for scraping, processing, and solving coding/math problems using AI-driven automation.

---

## 📖 Watch the video demo

<p align="center">
  <a href="https://www.youtube.com/watch?v=LNIItKA8Am8">
    <img src="https://img.youtube.com/vi/LNIItKA8Am8/hqdefault.jpg" alt="Watch the video" />
  </a>
</p>

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
conda create --name codemath_solver python=3.10
pip install -r requirements.txt

# Configure settings
cp .env.example .env  # Create config file
```

---

## 🏃♂️ Usage
```bash
# Run webUI with streamlit
streamlit run app.py --server.runOnSave true

# Run chrome debugging profile in port 9222
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="/tmp/ChromeProfile"
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

## 📌 License
Released under the [MIT License](LICENSE). Feel free to modify and distribute.

---

Made with ❤️ using Python and AI technologies
