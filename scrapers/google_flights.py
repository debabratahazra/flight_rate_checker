import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from utils.helpers import setup_driver, clean_price
from config import WAIT_TIME
from rich.console import Console

console = Console()

class GoogleFlightsScraper:
    
    def __init__(self):
        self.source = "Google Flights"
        self.base_url = "https://www.google.com/flights"
    
    def scrape(self, from_city: str, to_city: str, date: str) -> list:
        """
        Scrape flights from Google Flights
        
        Args:
            from_city: Departure city (e.g., "DEL")
            to_city: Destination city (e.g., "BOM")  
            date: Travel date (format: YYYY-MM-DD)
        
        Returns:
            List of flight dictionaries
        """
        driver = None
        flights = []
        
        try:
            console.print(f"[cyan]🔍 Scraping {self.source}...[/cyan]")
            driver = setup_driver()
            
            # Build Google Flights URL
            url = (
                f"https://www.google.com/travel/flights/search?"
                f"tfs=CBwQAhoeEgoyMDI0LTEyLTI1agcIARIDREVMcgcIARIDQk9N"
            )
            
            # Direct search URL format
            search_url = (
                f"https://www.google.com/flights#flt="
                f"{from_city}.{to_city}.{date};c:INR;e:1;sd:1;t:f"
            )
            
            driver.get(search_url)
            time.sleep(random.uniform(3, 5))
            
            # Wait for flight results
            wait = WebDriverWait(driver, WAIT_TIME)
            
            try:
                # Wait for flight cards to load
                wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "[data-ved]")
                    )
                )
                time.sleep(3)
                
            except TimeoutException:
                console.print(f"[yellow]⚠️ {self.source}: Page load timeout[/yellow]")
                return flights
            
            # Extract flight information
            flight_cards = driver.find_elements(
                By.CSS_SELECTOR, 
                "li.pIav2d, div[jsname='IWWDBc'], .YMlIz"
            )
            
            if not flight_cards:
                # Try alternative selectors
                flight_cards = driver.find_elements(
                    By.CSS_SELECTOR,
                    "[data-id], .gws-flights-results__result-item"
                )
            
            console.print(f"[green]Found {len(flight_cards)} results on {self.source}[/green]")
            
            for i, card in enumerate(flight_cards[:10]):  # Limit to 10 results
                try:
                    flight_data = self._extract_flight_data(card, i)
                    if flight_data:
                        flights.append(flight_data)
                except Exception as e:
                    continue
                    
        except Exception as e:
            console.print(f"[red]❌ {self.source} Error: {str(e)}[/red]")
            
        finally:
            if driver:
                driver.quit()
        
        return flights
    
    def _extract_flight_data(self, card, index: int) -> dict:
        """Extract flight data from a card element"""
        try:
            # Try multiple CSS selectors for different page layouts
            price = self._safe_extract(card, [
                ".YMlIz.FpEdX span",
                "[data-gs] .YMlIz",
                ".BVAVmf .YMlIz",
                "span[aria-label*='rupees']",
                ".U3gSDe .FpEdX"
            ])
            
            airline = self._safe_extract(card, [
                ".h1fkLb",
                ".sSHqwe.tPgKwe",
                ".Ir0Voe .sSHqwe",
                "[data-gs] .Ir0Voe"
            ])
            
            departure_time = self._safe_extract(card, [
                ".wtdjmc",
                ".Ir0Voe span[aria-label*='Departure']",
                ".zxVSec span"
            ])
            
            arrival_time = self._safe_extract(card, [
                ".XWcVob",
                "span[aria-label*='Arrival']"
            ])
            
            duration = self._safe_extract(card, [
                ".gvkrdb",
                ".AdWm1c.gvkrdb",
                "[aria-label*='duration']"
            ])
            
            stops = self._safe_extract(card, [
                ".EfT7Ae span",
                ".ogfYpf",
                "[aria-label*='stop']"
            ])
            
            if price and airline:
                return {
                    "source": self.source,
                    "airline": airline.strip(),
                    "price": clean_price(price),
                    "price_raw": price.strip(),
                    "departure_time": departure_time.strip() if departure_time else "N/A",
                    "arrival_time": arrival_time.strip() if arrival_time else "N/A",
                    "duration": duration.strip() if duration else "N/A",
                    "stops": stops.strip() if stops else "Non-stop",
                    "rank": index + 1
                }
        except Exception:
            pass
        return None
    
    def _safe_extract(self, element, selectors: list) -> str:
        """Try multiple selectors and return first successful result"""
        for selector in selectors:
            try:
                el = element.find_element(By.CSS_SELECTOR, selector)
                text = el.text or el.get_attribute("aria-label") or ""
                if text.strip():
                    return text
            except NoSuchElementException:
                continue
        return ""