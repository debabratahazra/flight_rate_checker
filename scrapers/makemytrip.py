import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from utils.helpers import setup_driver, clean_price
from config import WAIT_TIME
from rich.console import Console

console = Console()

class MakeMyTripScraper:
    
    def __init__(self):
        self.source = "MakeMyTrip"
        self.base_url = "https://www.makemytrip.com/flights"
    
    def scrape(self, from_city: str, to_city: str, date: str) -> list:
        """
        Scrape flights from MakeMyTrip
        Date format: MM/DD/YYYY
        """
        driver = None
        flights = []
        
        try:
            console.print(f"[cyan]🔍 Scraping {self.source}...[/cyan]")
            driver = setup_driver()
            
            # Format date MM/DD/YYYY
            parts = date.split("-")  # YYYY-MM-DD
            date_mmt = f"{parts[1]}/{parts[2]}/{parts[0]}"
            
            url = (
                f"https://www.makemytrip.com/flights/search?"
                f"itinerary={from_city}-{to_city}-{date_mmt}"
                f"&tripType=O&paxType=A-1_C-0_I-0"
                f"&intl=false&cabinClass=E&ccde=IN&lang=eng"
            )
            
            driver.get(url)
            time.sleep(random.uniform(5, 8))
            
            # Handle popups if any
            try:
                close_btn = driver.find_element(By.CSS_SELECTOR, ".commonModal__close, .fsw_popup_close")
                close_btn.click()
                time.sleep(1)
            except:
                pass
            
            wait = WebDriverWait(driver, WAIT_TIME + 5)
            
            try:
                wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".listingCard, .flight-info, [class*='FlightCard']")
                    )
                )
                time.sleep(3)
            except TimeoutException:
                console.print(f"[yellow]⚠️ {self.source}: Timeout[/yellow]")
                return flights
            
            # Scroll to load results
            for scroll in range(3):
                driver.execute_script(f"window.scrollTo(0, {(scroll+1)*400})")
                time.sleep(1)
            
            # Find flight cards
            flight_cards = driver.find_elements(
                By.CSS_SELECTOR,
                ".listingCard, [class*='ResultBlock'], .flight-listing-item"
            )
            
            console.print(f"[green]Found {len(flight_cards)} results on {self.source}[/green]")
            
            for i, card in enumerate(flight_cards[:10]):
                try:
                    flight_data = self._extract_flight_data(card, i)
                    if flight_data:
                        flights.append(flight_data)
                except Exception:
                    continue
                    
        except Exception as e:
            console.print(f"[red]❌ {self.source} Error: {str(e)}[/red]")
            
        finally:
            if driver:
                driver.quit()
        
        return flights
    
    def _extract_flight_data(self, card, index: int) -> dict:
        """Extract data from MMT flight card"""
        try:
            price = self._safe_find(card, [
                ".actual-price",
                "[class*='price-info'] strong",
                ".priceSection .amount",
                "[class*='Price'] span"
            ])
            
            airline = self._safe_find(card, [
                ".airlineName",
                "[class*='airline-name']",
                ".carrier .name",
                "[class*='AirlineName']"
            ])
            
            departure = self._safe_find(card, [
                ".departure .time",
                "[class*='depart'] [class*='time']",
                ".dp-time"
            ])
            
            arrival = self._safe_find(card, [
                ".arrival .time",
                "[class*='arrive'] [class*='time']",
                ".ar-time"
            ])
            
            duration = self._safe_find(card, [
                ".duration-section",
                "[class*='duration']",
                ".flt-duration"
            ])
            
            stops = self._safe_find(card, [
                ".num-stops",
                "[class*='stops']",
                ".stop-count"
            ])
            
            if price and airline:
                return {
                    "source": self.source,
                    "airline": airline.strip(),
                    "price": clean_price(price),
                    "price_raw": price.strip(),
                    "departure_time": departure.strip() if departure else "N/A",
                    "arrival_time": arrival.strip() if arrival else "N/A",
                    "duration": duration.strip() if duration else "N/A",
                    "stops": stops.strip() if stops else "N/A",
                    "rank": index + 1
                }
        except Exception:
            pass
        return None
    
    def _safe_find(self, element, selectors: list) -> str:
        for selector in selectors:
            try:
                el = element.find_element(By.CSS_SELECTOR, selector)
                if el.text.strip():
                    return el.text
            except:
                continue
        return ""