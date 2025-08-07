# tests/test_lqdoj.py
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def setup_driver():
    """Setup Chrome driver with fixed profile and download options"""
    options = webdriver.ChromeOptions()

    # Specify a fixed user profile directory
    profile_dir = "/Users/NghiaKhang/Coding/Projects/codemath-solver/chrome_profile"
    print(f"🔹 Profile directory: {profile_dir}")
    options.add_argument(f"--user-data-dir={profile_dir}")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Disable extensions, infobars, sandbox, and dev shm usage
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-infobars")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Set download directory and PDF handling
    download_dir = "/Users/NghiaKhang/Coding/Projects/codemath-solver/data"
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True,  # Force download PDFs instead of opening
    }
    options.add_experimental_option("prefs", prefs)

    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )
        # Remove webdriver property
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        print("✅ Browser driver created successfully with fixed profile")
        return driver
    except Exception as e:
        print(f"❌ Error creating browser driver: {str(e)}")
        raise


def test_lqdoj_with_selenium():
    driver = setup_driver()

    url = "https://lqdoj.edu.vn/problems/?page=1"
    driver.get(url)

    # Đợi Cloudflare challenge hoàn thành
    time.sleep(5)  # Tăng thời gian chờ
    print(f"Page title: {driver.title}")
    print(driver.page_source)

    # Kiểm tra xem có phải trang Cloudflare không
    if "Just a moment" in driver.page_source:
        print("❌ Still on Cloudflare challenge page")
    else:
        print("✅ Successfully bypassed Cloudflare")
        print("Page title:", driver.title)


test_lqdoj_with_selenium()
