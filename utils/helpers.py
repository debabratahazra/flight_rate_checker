import re
import os
import time
import random
import subprocess
import undetected_chromedriver as uc
from fake_useragent import UserAgent
from config import CHROME_OPTIONS, HEADLESS_MODE
from rich.console import Console

console = Console()

# undetected-chromedriver's __del__ raises a noisy (but harmless) OSError on
# Windows at interpreter shutdown ("WinError 6, The handle is invalid") because
# it tries to quit a driver whose process is already gone. Wrap the destructor
# once so that shutdown stays clean.
def _silence_uc_destructor():
    original_del = getattr(uc.Chrome, "__del__", None)
    if original_del is None or getattr(original_del, "_silenced", False):
        return

    def _quiet_del(self):
        try:
            original_del(self)
        except Exception:
            pass

    _quiet_del._silenced = True
    uc.Chrome.__del__ = _quiet_del

_silence_uc_destructor()


def _get_chrome_major_version():
    """
    Detect the installed Chrome major version so the matching ChromeDriver is
    downloaded. Returns an int (e.g. 148) or None if detection fails (in which
    case undetected-chromedriver falls back to auto-detection).
    """
    # Windows: read the version from the registry, then fall back to the binary.
    if os.name == "nt":
        try:
            import winreg
            for hive in (winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE):
                try:
                    key = winreg.OpenKey(hive, r"Software\Google\Chrome\BLBeacon")
                    version, _ = winreg.QueryValueEx(key, "version")
                    winreg.CloseKey(key)
                    if version:
                        return int(version.split(".")[0])
                except FileNotFoundError:
                    continue
        except Exception:
            pass

        for path in (
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        ):
            if os.path.exists(path):
                try:
                    out = subprocess.check_output(
                        [
                            "powershell", "-NoProfile", "-Command",
                            f"(Get-Item '{path}').VersionInfo.ProductVersion",
                        ],
                        text=True, stderr=subprocess.DEVNULL,
                    ).strip()
                    if out:
                        return int(out.split(".")[0])
                except Exception:
                    continue
        return None

    # POSIX: ask the Chrome/Chromium binary for its version.
    for binary in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        try:
            out = subprocess.check_output([binary, "--version"], text=True, stderr=subprocess.DEVNULL).strip()
            match = re.search(r"(\d+)\.", out)
            if match:
                return int(match.group(1))
        except Exception:
            continue
    return None

def setup_driver():
    """Setup undetected Chrome driver to avoid bot detection"""
    
    options = uc.ChromeOptions()
    
    if HEADLESS_MODE:
        options.add_argument("--headless=new")
    
    for option in CHROME_OPTIONS:
        options.add_argument(option)
    
    # Random user agent
    try:
        ua = UserAgent()
        options.add_argument(f"user-agent={ua.random}")
    except:
        pass
    
    # Additional stealth settings
    options.add_argument("--lang=en-IN")
    options.add_argument("--accept-language=en-IN,en;q=0.9")
    
    # Match ChromeDriver to the installed Chrome's major version. Passing None
    # makes undetected-chromedriver fetch the newest driver, which fails when the
    # local Chrome lags behind ("only supports Chrome version N").
    chrome_version = _get_chrome_major_version()

    try:
        driver = uc.Chrome(
            options=options,
            version_main=chrome_version,
            use_subprocess=True
        )
        
        # Set window size
        driver.set_window_size(1920, 1080)
        
        # Execute stealth scripts
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        
        return driver
        
    except Exception as e:
        console.print(f"[red]Driver setup error: {e}[/red]")
        raise

def clean_price(price_str: str) -> int:
    """
    Extract numeric price from string
    Example: "₹3,499" -> 3499
    """
    if not price_str:
        return 999999
    
    # Remove currency symbols and commas
    cleaned = re.sub(r'[₹,\s,Rs.,INR]', '', price_str)
    
    # Extract numbers only
    numbers = re.findall(r'\d+', cleaned)
    
    if numbers:
        # Join if price is split
        price = int(''.join(numbers[:2]) if len(''.join(numbers[:2])) <= 6 else numbers[0])
        return price
    
    return 999999

def format_date_display(date_str: str) -> str:
    """Format date for display: 2024-12-25 -> 25 Dec 2024"""
    from datetime import datetime
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d %B %Y")
    except:
        return date_str

def get_airport_code(city: str, airport_codes: dict) -> str:
    """Get IATA airport code for city"""
    city_lower = city.lower().strip()
    
    # Direct match
    if city_lower in airport_codes:
        return airport_codes[city_lower]
    
    # Partial match
    for key, code in airport_codes.items():
        if city_lower in key or key in city_lower:
            return code
    
    # Return as-is if 3 letters (assume already a code)
    if len(city) == 3:
        return city.upper()
    
    return city.upper()

def random_delay(min_sec: float = 1.0, max_sec: float = 3.0):
    """Add random delay to avoid detection"""
    time.sleep(random.uniform(min_sec, max_sec))

def validate_date(date_str: str) -> bool:
    """Validate date format YYYY-MM-DD"""
    from datetime import datetime, date
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = date.today()
        if dt < today:
            console.print("[red]❌ Date cannot be in the past![/red]")
            return False
        return True
    except ValueError:
        console.print("[red]❌ Invalid date format! Use YYYY-MM-DD[/red]")
        return False