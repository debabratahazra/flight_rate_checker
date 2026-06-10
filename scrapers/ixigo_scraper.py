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

class IxigoScraper:
    
    def __init__(self):
        self.source = "Ixigo"
        self.base_url = "https://www.ixigo.com/search/result/flight"
    
    def scrape(self, from_city: str, to_city: str, date: str) -> list:
        """
        Scrape flights from Ixigo
        Date format: YYYYMMDD
        """
        driver = None
        flights = []
        
        try:
            console.print(f"[cyan]🔍 Scraping {self.source}...[/cyan]")
            driver = setup_driver()
            
            # Format date for Ixigo (YYYYMMDD)
            date_formatted = date.replace("-", "")
            
            url = (
                f"https://www.ixigo.com/search/result/flight"
                f"?from={from_city}"
                f"&to={to_city}"
                f"&date={date_formatted}"
                f"&adults=1&children=0&infants=0"
                f"&class=e&source=Search"
            )
            
            driver.get(url)
            time.sleep(random.uniform(4, 6))
            
            wait = WebDriverWait(driver, WAIT_TIME + 5)
            
            try:
                # Wait for flight results container
                wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".flight-listing, .flightSearchResult, .u-pointer")
                    )
                )
                time.sleep(3)
                
            except TimeoutException:
                console.print(f"[yellow]⚠️ {self.source}: Timeout waiting for results[/yellow]")
                return flights
            
            # Scroll to load more results
            driver.execute_script("window.scrollTo(0, 500)")
            time.sleep(2)
            
            # Find flight cards
            flight_cards = driver.find_elements(
                By.CSS_SELECTOR,
                ".flight-listing li, .flight-card, .SearchResult__FlightCard"
            )
            
            if not flight_cards:
                flight_cards = driver.find_elements(
                    By.CSS_SELECTOR,
                    "[class*='flight-card'], [class*='FlightCard'], .u-pointer"
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
        """Extract data from Ixigo flight card"""
        try:
            price = self._safe_find(card, [
                ".fare .price",
                "[class*='price']",
                ".u-font-24",
                ".fare-details .price",
                "[class*='fare'] strong"
            ])
            
            airline = self._safe_find(card, [
                ".airline-name",
                "[class*='airline']",
                ".carrier-name",
                ".u-font-bold"
            ])
            
            departure = self._safe_find(card, [
                ".departure .time",
                "[class*='departure'] [class*='time']",
                ".dep-time"
            ])
            
            arrival = self._safe_find(card, [
                ".arrival .time",
                "[class*='arrival'] [class*='time']",
                ".arr-time"
            ])
            
            duration = self._safe_find(card, [
                ".duration",
                "[class*='duration']",
                ".travel-time"
            ])
            
            stops = self._safe_find(card, [
                ".stops",
                "[class*='stop']",
                ".via-stops"
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
        """Try multiple selectors"""
        for selector in selectors:
            try:
                el = element.find_element(By.CSS_SELECTOR, selector)
                if el.text.strip():
                    return el.text
            except:
                continue
        return ""