# ============================================================
# user_input/input_handler.py
# Complete Interactive User Input Handler
# ============================================================

from datetime import datetime, date, timedelta
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.columns import Columns
from rich import print as rprint
from rich.text import Text
from config import AIRPORT_CODES

console = Console()

# ============================================================
# ALL INDIAN AIRPORTS - Full List
# ============================================================
AIRPORTS = {
    # Format: "code": {"city": "", "name": "", "state": ""}
    
    # Metro Cities
    "DEL": {"city": "Delhi",          "name": "Indira Gandhi International Airport",     "state": "Delhi"},
    "BOM": {"city": "Mumbai",         "name": "Chhatrapati Shivaji Maharaj Intl Airport","state": "Maharashtra"},
    "BLR": {"city": "Bangalore",      "name": "Kempegowda International Airport",        "state": "Karnataka"},
    "MAA": {"city": "Chennai",        "name": "Chennai International Airport",           "state": "Tamil Nadu"},
    "CCU": {"city": "Kolkata",        "name": "Netaji Subhas Chandra Bose Intl Airport", "state": "West Bengal"},
    "HYD": {"city": "Hyderabad",      "name": "Rajiv Gandhi International Airport",      "state": "Telangana"},
    
    # Popular Cities
    "GOI": {"city": "Goa",            "name": "Goa International Airport (Dabolim)",     "state": "Goa"},
    "PNQ": {"city": "Pune",           "name": "Pune Airport",                            "state": "Maharashtra"},
    "AMD": {"city": "Ahmedabad",      "name": "Sardar Vallabhbhai Patel Intl Airport",   "state": "Gujarat"},
    "JAI": {"city": "Jaipur",         "name": "Jaipur International Airport",            "state": "Rajasthan"},
    "COK": {"city": "Kochi",          "name": "Cochin International Airport",            "state": "Kerala"},
    "LKO": {"city": "Lucknow",        "name": "Chaudhary Charan Singh Intl Airport",     "state": "Uttar Pradesh"},
    "IXC": {"city": "Chandigarh",     "name": "Chandigarh International Airport",        "state": "Punjab"},
    "NAG": {"city": "Nagpur",         "name": "Dr. Babasaheb Ambedkar Intl Airport",     "state": "Maharashtra"},
    "IDR": {"city": "Indore",         "name": "Devi Ahilyabai Holkar Airport",           "state": "Madhya Pradesh"},
    "ATQ": {"city": "Amritsar",       "name": "Sri Guru Ram Dass Jee Intl Airport",      "state": "Punjab"},
    "SXR": {"city": "Srinagar",       "name": "Sheikh ul-Alam International Airport",    "state": "J&K"},
    "IXL": {"city": "Leh",            "name": "Kushok Bakula Rimpochee Airport",         "state": "Ladakh"},
    "GAU": {"city": "Guwahati",       "name": "Lokpriya Gopinath Bordoloi Intl Airport", "state": "Assam"},
    "BBI": {"city": "Bhubaneswar",    "name": "Biju Patnaik International Airport",      "state": "Odisha"},
    "VTZ": {"city": "Visakhapatnam",  "name": "Visakhapatnam Airport",                   "state": "Andhra Pradesh"},
    "CJB": {"city": "Coimbatore",     "name": "Coimbatore International Airport",        "state": "Tamil Nadu"},
    "IXM": {"city": "Madurai",        "name": "Madurai Airport",                         "state": "Tamil Nadu"},
    "TRZ": {"city": "Tiruchirappalli","name": "Tiruchirappalli International Airport",    "state": "Tamil Nadu"},
    "IXE": {"city": "Mangalore",      "name": "Mangaluru International Airport",         "state": "Karnataka"},
    "IXR": {"city": "Ranchi",         "name": "Birsa Munda Airport",                     "state": "Jharkhand"},
    "RPR": {"city": "Raipur",         "name": "Swami Vivekananda Airport",               "state": "Chhattisgarh"},
    "PAT": {"city": "Patna",          "name": "Jay Prakash Narayan Airport",             "state": "Bihar"},
    "VNS": {"city": "Varanasi",       "name": "Lal Bahadur Shastri Airport",             "state": "Uttar Pradesh"},
    "BHO": {"city": "Bhopal",         "name": "Raja Bhoj Airport",                       "state": "Madhya Pradesh"},
    "TRV": {"city": "Thiruvananthapuram","name": "Trivandrum International Airport",     "state": "Kerala"},
    "IXZ": {"city": "Port Blair",     "name": "Veer Savarkar International Airport",     "state": "Andaman"},
    "DED": {"city": "Dehradun",       "name": "Jolly Grant Airport",                     "state": "Uttarakhand"},
    "SHL": {"city": "Shillong",       "name": "Shillong Airport",                        "state": "Meghalaya"},
    "IMP": {"city": "Imphal",         "name": "Bir Tikendrajit International Airport",   "state": "Manipur"},
    "AGX": {"city": "Agartala",       "name": "Maharaja Bir Bikram Airport",             "state": "Tripura"},
    "DIB": {"city": "Dibrugarh",      "name": "Dibrugarh Airport",                       "state": "Assam"},
    "JRH": {"city": "Jorhat",         "name": "Jorhat Airport",                          "state": "Assam"},
    "IXS": {"city": "Silchar",        "name": "Silchar Airport",                         "state": "Assam"},
    "KNU": {"city": "Kanpur",         "name": "Kanpur Airport",                          "state": "Uttar Pradesh"},
    "AGR": {"city": "Agra",           "name": "Agra Airport",                            "state": "Uttar Pradesh"},
    "UDR": {"city": "Udaipur",        "name": "Maharana Pratap Airport",                 "state": "Rajasthan"},
    "JSA": {"city": "Jaisalmer",      "name": "Jaisalmer Airport",                       "state": "Rajasthan"},
    "JDH": {"city": "Jodhpur",        "name": "Jodhpur Airport",                         "state": "Rajasthan"},
    "BKB": {"city": "Bikaner",        "name": "Nal Airport",                             "state": "Rajasthan"},
    "GWL": {"city": "Gwalior",        "name": "Gwalior Airport",                         "state": "Madhya Pradesh"},
    "JLR": {"city": "Jabalpur",       "name": "Jabalpur Airport",                        "state": "Madhya Pradesh"},
    "STV": {"city": "Surat",          "name": "Surat Airport",                           "state": "Gujarat"},
    "BDQ": {"city": "Vadodara",       "name": "Vadodara Airport",                        "state": "Gujarat"},
    "RAJ": {"city": "Rajkot",         "name": "Rajkot Airport",                          "state": "Gujarat"},
    "BHJ": {"city": "Bhuj",           "name": "Bhuj Airport",                            "state": "Gujarat"},
    "HBX": {"city": "Hubli",          "name": "Hubli Airport",                           "state": "Karnataka"},
    "BEP": {"city": "Bellary",        "name": "Bellary Airport",                         "state": "Karnataka"},
    "IXG": {"city": "Belgaum",        "name": "Belgaum Airport",                         "state": "Karnataka"},
    "CNN": {"city": "Kannur",         "name": "Kannur International Airport",            "state": "Kerala"},
    "KJB": {"city": "Kalaburagi",     "name": "Kalaburagi Airport",                      "state": "Karnataka"},
}

# Time Frame Options
TIME_FRAMES = {
    "1": {"label": "Early Morning", "range": "00:00 - 06:00", "start": 0,  "end": 6},
    "2": {"label": "Morning",       "range": "06:00 - 12:00", "start": 6,  "end": 12},
    "3": {"label": "Afternoon",     "range": "12:00 - 17:00", "start": 12, "end": 17},
    "4": {"label": "Evening",       "range": "17:00 - 21:00", "start": 17, "end": 21},
    "5": {"label": "Night",         "range": "21:00 - 24:00", "start": 21, "end": 24},
    "6": {"label": "Any Time",      "range": "All Day",        "start": 0,  "end": 24},
}

# Travel Class Options
TRAVEL_CLASS = {
    "1": {"label": "Economy",         "code": "E",  "icon": "💺"},
    "2": {"label": "Premium Economy", "code": "PE", "icon": "💺✨"},
    "3": {"label": "Business",        "code": "B",  "icon": "🛋️"},
    "4": {"label": "First Class",     "code": "F",  "icon": "👑"},
}

# Passenger Types
MAX_PASSENGERS = {
    "adults":   {"min": 1, "max": 9,  "label": "Adults (12+ years)"},
    "children": {"min": 0, "max": 8,  "label": "Children (2-11 years)"},
    "infants":  {"min": 0, "max": 4,  "label": "Infants (Under 2 years)"},
}

# ============================================================
# DISPLAY FUNCTIONS
# ============================================================

def show_welcome_banner():
    """Display welcome banner"""
    
    banner_text = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║          ✈️   INDIA DOMESTIC FLIGHT FINDER   ✈️              ║
    ║                                                              ║
    ║        🤖 Powered by Web Scraping + AI/LLM                  ║
    ║        🔍 Searches 10+ Flight Websites                       ║
    ║        💰 Finds You The Cheapest Deal!                       ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    console.print(Panel(banner_text, style="bold blue", padding=(0, 2)))

def show_airport_list():
    """Display all available airports in a table"""
    
    console.print("\n[bold yellow]📍 Available Airports in India:[/bold yellow]\n")
    
    # Group airports by state/region
    table = Table(
        title="🛫 All Available Indian Airports",
        show_header=True,
        header_style="bold cyan",
        border_style="blue",
        show_lines=False,
        padding=(0, 1)
    )
    
    table.add_column("Code",    style="bold yellow", width=6)
    table.add_column("City",    style="bold white",  width=18)
    table.add_column("Airport", style="dim white",   width=35)
    table.add_column("State",   style="cyan",        width=20)
    
    for code, info in AIRPORTS.items():
        table.add_row(
            code,
            info["city"],
            info["name"][:34],
            info["state"]
        )
    
    console.print(table)

def show_popular_routes():
    """Show popular domestic routes"""
    
    popular_routes = [
        ("DEL", "BOM", "Delhi → Mumbai",        "Most Popular"),
        ("DEL", "BLR", "Delhi → Bangalore",     "Highly Traveled"),
        ("BOM", "GOI", "Mumbai → Goa",          "Weekend Special"),
        ("DEL", "GOI", "Delhi → Goa",           "Tourist Favorite"),
        ("BOM", "BLR", "Mumbai → Bangalore",    "Business Route"),
        ("DEL", "HYD", "Delhi → Hyderabad",     "Popular Route"),
        ("BLR", "HYD", "Bangalore → Hyderabad", "Short Hop"),
        ("BOM", "COK", "Mumbai → Kochi",        "Popular"),
        ("DEL", "JAI", "Delhi → Jaipur",        "Weekend Getaway"),
        ("DEL", "SXR", "Delhi → Srinagar",      "Scenic Route"),
        ("DEL", "IXL", "Delhi → Leh",           "Adventure Route"),
        ("MAA", "BOM", "Chennai → Mumbai",      "Business Route"),
    ]
    
    console.print("\n[bold yellow]🌟 Popular Domestic Routes:[/bold yellow]\n")
    
    table = Table(
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        show_lines=False,
        padding=(0, 2)
    )
    
    table.add_column("From", style="bold yellow", width=5)
    table.add_column("To",   style="bold yellow", width=5)
    table.add_column("Route",  style="bold white",  width=25)
    table.add_column("Type",   style="green",       width=20)
    
    for route in popular_routes:
        table.add_row(route[0], route[1], route[2], route[3])
    
    console.print(table)
    console.print("[dim]Enter airport code (e.g., DEL, BOM, BLR)[/dim]\n")

# ============================================================
# INPUT FUNCTIONS
# ============================================================

def get_airport_input(prompt_text: str, exclude_code: str = None) -> dict:
    """
    Get airport input from user with validation
    
    Returns:
        dict with code, city, name info
    """
    while True:
        console.print(f"\n[bold cyan]{prompt_text}[/bold cyan]")
        console.print("[dim]Enter airport code (e.g., DEL) or city name (e.g., Delhi)[/dim]")
        
        # Show option to see all airports
        show_list = Confirm.ask(
            "[dim]Show airport list?[/dim]", 
            default=False
        )
        
        if show_list:
            show_airport_list()
            show_popular_routes()
        
        user_input = Prompt.ask(
            f"[yellow]✈️  {prompt_text}[/yellow]"
        ).strip().upper()
        
        # Check if it's a direct airport code
        if user_input in AIRPORTS:
            airport = AIRPORTS[user_input]
            if exclude_code and user_input == exclude_code:
                console.print("[red]❌ Source and destination cannot be the same![/red]")
                continue
            
            console.print(
                f"[green]✅ Selected: {user_input} - {airport['city']} "
                f"({airport['name']})[/green]"
            )
            return {
                "code": user_input,
                "city": airport["city"],
                "name": airport["name"],
                "state": airport["state"]
            }
        
        # Try city name search
        matches = []
        for code, info in AIRPORTS.items():
            if (user_input.lower() in info["city"].lower() or
                user_input.lower() in info["name"].lower() or
                user_input.lower() in info["state"].lower()):
                matches.append((code, info))
        
        if len(matches) == 1:
            code, airport = matches[0]
            if exclude_code and code == exclude_code:
                console.print("[red]❌ Source and destination cannot be the same![/red]")
                continue
            console.print(
                f"[green]✅ Found: {code} - {airport['city']} "
                f"({airport['name']})[/green]"
            )
            return {
                "code": code,
                "city": airport["city"],
                "name": airport["name"],
                "state": airport["state"]
            }
        
        elif len(matches) > 1:
            console.print(f"\n[yellow]Multiple airports found for '{user_input}':[/yellow]")
            
            table = Table(show_header=True, header_style="bold cyan", 
                         border_style="dim", padding=(0,1))
            table.add_column("#",    width=4)
            table.add_column("Code", style="bold yellow", width=6)
            table.add_column("City", style="bold white",  width=18)
            table.add_column("Airport Name", style="dim", width=35)
            table.add_column("State", style="cyan",       width=18)
            
            for idx, (code, info) in enumerate(matches, 1):
                table.add_row(
                    str(idx), code, info["city"],
                    info["name"][:34], info["state"]
                )
            
            console.print(table)
            
            choice = Prompt.ask(
                "[yellow]Select airport number[/yellow]",
                choices=[str(i) for i in range(1, len(matches)+1)]
            )
            
            code, airport = matches[int(choice) - 1]
            
            if exclude_code and code == exclude_code:
                console.print("[red]❌ Source and destination cannot be the same![/red]")
                continue
                
            return {
                "code": code,
                "city": airport["city"],
                "name": airport["name"],
                "state": airport["state"]
            }
        
        else:
            console.print(f"[red]❌ Airport '{user_input}' not found![/red]")
            console.print("[yellow]Tip: Type 'LIST' to see all airports[/yellow]")

def get_date_input(prompt_text: str, min_date: date = None) -> str:
    """
    Get date input with validation
    
    Returns:
        Date string in YYYY-MM-DD format
    """
    today = date.today()
    
    if min_date is None:
        min_date = today
    
    console.print(f"\n[bold cyan]{prompt_text}[/bold cyan]")
    
    # Show quick date options
    console.print("\n[dim]Quick Options:[/dim]")
    
    quick_dates = Table(show_header=False, border_style="dim", padding=(0, 2))
    quick_dates.add_column("Option", style="yellow", width=4)
    quick_dates.add_column("Label",  style="white",  width=15)
    quick_dates.add_column("Date",   style="cyan",   width=15)
    
    quick_options = {
        "1": ("Today",        today),
        "2": ("Tomorrow",     today + timedelta(days=1)),
        "3": ("This Weekend", today + timedelta(days=(5-today.weekday()) % 7)),
        "4": ("Next Week",    today + timedelta(weeks=1)),
        "5": ("2 Weeks",      today + timedelta(weeks=2)),
        "6": ("1 Month",      today + timedelta(days=30)),
        "7": ("Custom Date",  None),
    }
    
    for key, (label, dt) in quick_options.items():
        date_str = dt.strftime("%d %b %Y (%A)") if dt else "Enter manually"
        quick_dates.add_row(key, label, date_str)
    
    console.print(quick_dates)
    
    choice = Prompt.ask(
        "[yellow]Select option or enter custom date (YYYY-MM-DD)[/yellow]",
        default="7"
    )
    
    # Handle quick options
    if choice in quick_options and choice != "7":
        selected_date = quick_options[choice][1]
        if selected_date < min_date:
            console.print(f"[red]❌ Date cannot be before {min_date}[/red]")
            return get_date_input(prompt_text, min_date)
        result = selected_date.strftime("%Y-%m-%d")
        console.print(f"[green]✅ Date selected: {selected_date.strftime('%d %B %Y (%A)')}[/green]")
        return result
    
    # Custom date input
    while True:
        if choice == "7" or choice not in quick_options:
            custom = Prompt.ask(
                "[yellow]Enter date (YYYY-MM-DD)[/yellow]",
                default=(today + timedelta(days=7)).strftime("%Y-%m-%d")
            )
        else:
            custom = choice
        
        try:
            selected_date = datetime.strptime(custom, "%Y-%m-%d").date()
            
            if selected_date < min_date:
                console.print(f"[red]❌ Date cannot be in the past! Min date: {min_date}[/red]")
                continue
            
            if selected_date > today + timedelta(days=365):
                console.print("[red]❌ Date too far in future (max 1 year ahead)[/red]")
                continue
            
            console.print(
                f"[green]✅ Date selected: "
                f"{selected_date.strftime('%d %B %Y (%A)')}[/green]"
            )
            return custom
            
        except ValueError:
            console.print("[red]❌ Invalid format! Use YYYY-MM-DD (e.g., 2025-03-15)[/red]")

def get_trip_type() -> str:
    """
    Get trip type: One-way or Round-trip
    
    Returns:
        "oneway" or "roundtrip"
    """
    console.print("\n[bold cyan]🔄 Trip Type:[/bold cyan]\n")
    
    table = Table(show_header=False, border_style="dim", padding=(0, 3))
    table.add_column("Option", style="bold yellow", width=4)
    table.add_column("Type",   style="bold white",  width=15)
    table.add_column("Desc",   style="dim",         width=35)
    
    table.add_row("1", "✈️  One Way",    "Single trip from source to destination")
    table.add_row("2", "🔄 Round Trip", "Return journey included (cheaper fares!)")
    
    console.print(table)
    
    choice = Prompt.ask(
        "[yellow]Select trip type[/yellow]",
        choices=["1", "2"],
        default="1"
    )
    
    trip_type = "oneway" if choice == "1" else "roundtrip"
    label = "One Way ✈️" if trip_type == "oneway" else "Round Trip 🔄"
    console.print(f"[green]✅ Trip type: {label}[/green]")
    
    return trip_type

def get_time_frame() -> dict:
    """
    Get preferred time frame for departure
    
    Returns:
        dict with time frame details
    """
    console.print("\n[bold cyan]⏰ Preferred Departure Time:[/bold cyan]\n")
    
    table = Table(show_header=True, header_style="bold cyan",
                 border_style="dim", padding=(0, 2))
    table.add_column("Option", style="bold yellow", width=6)
    table.add_column("Time Frame", style="bold white", width=16)
    table.add_column("Hours", style="cyan", width=15)
    table.add_column("Best For", style="dim", width=30)
    
    best_for = {
        "1": "Cheapest fares, good for budget travel",
        "2": "Business travelers, full day ahead",
        "3": "Leisure travelers, convenient timing",
        "4": "Office goers, after work travel",
        "5": "Night owls, next-day arrival",
        "6": "No preference, all flights shown",
    }
    
    for key, tf in TIME_FRAMES.items():
        table.add_row(
            key,
            tf["label"],
            tf["range"],
            best_for[key]
        )
    
    console.print(table)
    
    choice = Prompt.ask(
        "[yellow]Select preferred departure time[/yellow]",
        choices=list(TIME_FRAMES.keys()),
        default="6"
    )
    
    selected = TIME_FRAMES[choice]
    console.print(f"[green]✅ Time frame: {selected['label']} ({selected['range']})[/green]")
    
    return {
        "choice": choice,
        "label": selected["label"],
        "range": selected["range"],
        "start_hour": selected["start"],
        "end_hour": selected["end"]
    }

def get_passengers() -> dict:
    """
    Get passenger counts
    
    Returns:
        dict with adults, children, infants count
    """
    console.print("\n[bold cyan]👥 Passenger Details:[/bold cyan]\n")
    
    passengers = {}
    
    # Adults
    console.print("[dim]Adults: Passengers 12 years and above[/dim]")
    adults = IntPrompt.ask(
        "[yellow]Number of Adults[/yellow]",
        default=1
    )
    while adults < 1 or adults > 9:
        console.print("[red]❌ Adults must be between 1 and 9[/red]")
        adults = IntPrompt.ask("[yellow]Number of Adults[/yellow]", default=1)
    passengers["adults"] = adults
    
    # Children
    console.print("[dim]Children: Passengers between 2-11 years[/dim]")
    children = IntPrompt.ask(
        "[yellow]Number of Children (2-11 yrs)[/yellow]",
        default=0
    )
    while children < 0 or children > 8:
        console.print("[red]❌ Children must be between 0 and 8[/red]")
        children = IntPrompt.ask("[yellow]Number of Children[/yellow]", default=0)
    passengers["children"] = children
    
    # Infants
    console.print("[dim]Infants: Passengers under 2 years[/dim]")
    infants = IntPrompt.ask(
        "[yellow]Number of Infants (under 2 yrs)[/yellow]",
        default=0
    )
    while infants < 0 or infants > adults:
        console.print(f"[red]❌ Infants ({infants}) cannot exceed Adults ({adults})[/red]")
        infants = IntPrompt.ask("[yellow]Number of Infants[/yellow]", default=0)
    passengers["infants"] = infants
    
    total = adults + children
    console.print(
        f"[green]✅ Passengers: {adults} Adult(s), "
        f"{children} Child(ren), {infants} Infant(s) "
        f"[Total: {total}][/green]"
    )
    
    return passengers

def get_travel_class() -> dict:
    """
    Get preferred travel class
    
    Returns:
        dict with class label and code
    """
    console.print("\n[bold cyan]💺 Travel Class:[/bold cyan]\n")
    
    table = Table(show_header=True, header_style="bold cyan",
                 border_style="dim", padding=(0, 2))
    table.add_column("Option", style="bold yellow", width=6)
    table.add_column("Class",  style="bold white",  width=18)
    table.add_column("Features", style="dim",       width=40)
    
    features = {
        "1": "Standard seating, basic amenities, cheapest fares",
        "2": "Extra legroom, enhanced meals, priority boarding",
        "3": "Wider seats, premium meals, lounge access",
        "4": "Private suite, luxury dining, exclusive services",
    }
    
    for key, cls in TRAVEL_CLASS.items():
        table.add_row(
            key,
            f"{cls['icon']} {cls['label']}",
            features[key]
        )
    
    console.print(table)
    
    choice = Prompt.ask(
        "[yellow]Select travel class[/yellow]",
        choices=list(TRAVEL_CLASS.keys()),
        default="1"
    )
    
    selected = TRAVEL_CLASS[choice]
    console.print(f"[green]✅ Travel class: {selected['icon']} {selected['label']}[/green]")
    
    return {
        "label": selected["label"],
        "code": selected["code"],
        "icon": selected["icon"]
    }

def get_preferences() -> dict:
    """
    Get user preferences for flight search
    
    Returns:
        dict with all preferences
    """
    console.print("\n[bold cyan]⚙️  Search Preferences:[/bold cyan]\n")
    
    # Priority
    console.print("[dim]What matters most to you?[/dim]")
    
    pref_table = Table(show_header=False, border_style="dim", padding=(0, 2))
    pref_table.add_column("Opt", style="yellow", width=4)
    pref_table.add_column("Priority", style="bold white", width=15)
    pref_table.add_column("Description", style="dim", width=40)
    
    pref_table.add_row("1", "💰 Cheapest Price",  "Find the absolute lowest fare")
    pref_table.add_row("2", "⚡ Fastest Flight",  "Shortest travel duration")
    pref_table.add_row("3", "🛫 Non-stop Only",   "Direct flights only, no layovers")
    pref_table.add_row("4", "⭐ Best Overall",    "Balance of price, time & comfort")
    
    console.print(pref_table)
    
    priority_map = {
        "1": "price",
        "2": "speed",
        "3": "nonstop",
        "4": "best_overall"
    }
    
    priority_choice = Prompt.ask(
        "[yellow]Your priority[/yellow]",
        choices=["1", "2", "3", "4"],
        default="4"
    )
    priority = priority_map[priority_choice]
    
    # Max Budget
    console.print("\n[dim]Maximum budget per person (INR):[/dim]")
    budget_input = Prompt.ask(
        "[yellow]Max Budget (INR) [Press Enter to skip][/yellow]",
        default=""
    )
    max_budget = int(budget_input) if budget_input.isdigit() else None
    
    # Airlines preference
    console.print("\n[dim]Preferred airlines (optional):[/dim]")
    
    airline_table = Table(show_header=False, border_style="dim", padding=(0, 2))
    airline_table.add_column("Opt", style="yellow", width=4)
    airline_table.add_column("Airline", style="bold white", width=20)
    airline_table.add_column("Type", style="dim", width=20)
    
    airline_table.add_row("1", "✈️  IndiGo",      "Low Cost Carrier")
    airline_table.add_row("2", "🌶️  SpiceJet",    "Low Cost Carrier")
    airline_table.add_row("3", "🇮🇳 Air India",   "Full Service")
    airline_table.add_row("4", "🟤 Akasa Air",    "New Low Cost")
    airline_table.add_row("5", "All Airlines",   "No preference")
    
    console.print(airline_table)
    
    airline_map = {
        "1": "IndiGo",
        "2": "SpiceJet",
        "3": "Air India",
        "4": "Akasa Air",
        "5": None
    }
    
    airline_choice = Prompt.ask(
        "[yellow]Preferred airline[/yellow]",
        choices=["1", "2", "3", "4", "5"],
        default="5"
    )
    preferred_airline = airline_map[airline_choice]
    
    # Non-stop only
    nonstop_only = False
    if priority != "nonstop":
        nonstop_only = Confirm.ask(
            "[yellow]Non-stop flights only?[/yellow]",
            default=False
        )
    else:
        nonstop_only = True
    
    return {
        "priority": priority,
        "max_budget": max_budget,
        "preferred_airline": preferred_airline,
        "nonstop_only": nonstop_only
    }

def show_search_summary(search_params: dict):
    """
    Display complete search summary before starting
    """
    console.print("\n")
    
    # Build summary content
    source = search_params["source"]
    dest   = search_params["destination"]
    
    trip_type_label = "One Way ✈️" if search_params["trip_type"] == "oneway" else "Round Trip 🔄"
    
    pax = search_params["passengers"]
    pax_str = (
        f"{pax['adults']} Adult(s)"
        + (f", {pax['children']} Child(ren)" if pax['children'] > 0 else "")
        + (f", {pax['infants']} Infant(s)" if pax['infants'] > 0 else "")
    )
    
    prefs = search_params["preferences"]
    
    summary = (
        f"[bold white]─── FLIGHT SEARCH DETAILS ───[/bold white]\n\n"
        
        f"[cyan]🛫 FROM:[/cyan]  [bold]{source['city']} ({source['code']})[/bold]\n"
        f"         {source['name']}\n"
        f"         {source['state']}\n\n"
        
        f"[cyan]🛬 TO:[/cyan]    [bold]{dest['city']} ({dest['code']})[/bold]\n"
        f"         {dest['name']}\n"
        f"         {dest['state']}\n\n"
        
        f"[cyan]📅 DATE:[/cyan]  [bold]{search_params['depart_date_display']}[/bold]\n"
    )
    
    if search_params["trip_type"] == "roundtrip":
        summary += (
            f"[cyan]📅 RETURN:[/cyan] [bold]{search_params.get('return_date_display', 'N/A')}[/bold]\n"
        )
    
    summary += (
        f"\n[cyan]🔄 TRIP:[/cyan]  [bold]{trip_type_label}[/bold]\n"
        f"[cyan]⏰ TIME:[/cyan]  [bold]{search_params['time_frame']['label']} "
        f"({search_params['time_frame']['range']})[/bold]\n"
        f"[cyan]👥 PAX:[/cyan]   [bold]{pax_str}[/bold]\n"
        f"[cyan]💺 CLASS:[/cyan] [bold]{search_params['travel_class']['icon']} "
        f"{search_params['travel_class']['label']}[/bold]\n\n"
        
        f"[cyan]⚙️  PREFERENCES:[/cyan]\n"
        f"  Priority: [bold]{prefs['priority'].replace('_', ' ').title()}[/bold]\n"
    )
    
    if prefs.get("max_budget"):
        summary += f"  Max Budget: [bold green]₹{prefs['max_budget']:,}[/bold green]\n"
    
    if prefs.get("preferred_airline"):
        summary += f"  Airline: [bold]{prefs['preferred_airline']}[/bold]\n"
    
    summary += (
        f"  Non-stop Only: [bold]"
        f"{'Yes ✅' if prefs.get('nonstop_only') else 'No'}[/bold]\n"
    )
    
    console.print(Panel(summary, title="✈️ YOUR FLIGHT SEARCH", border_style="bold blue"))

# ============================================================
# MAIN INPUT COLLECTION FUNCTION
# ============================================================

def collect_all_inputs() -> dict:
    """
    Main function to collect ALL user inputs
    
    Returns:
        Complete search parameters dictionary
    """
    
    # Welcome Banner
    show_welcome_banner()
    
    console.print("\n[bold green]Let's find you the best flight deal! 🎯[/bold green]")
    console.print("[dim]Fill in the details below step by step...[/dim]\n")
    console.print("─" * 60)
    
    # ── STEP 1: SOURCE AIRPORT ──────────────────────────────
    console.print("\n[bold white]STEP 1 of 7 → Source Airport[/bold white]")
    show_popular_routes()
    source_airport = get_airport_input("🛫 From (Departure Airport)")
    
    # ── STEP 2: DESTINATION AIRPORT ─────────────────────────
    console.print("\n[bold white]STEP 2 of 7 → Destination Airport[/bold white]")
    dest_airport = get_airport_input(
        "🛬 To (Destination Airport)",
        exclude_code=source_airport["code"]
    )
    
    # ── STEP 3: TRIP TYPE ────────────────────────────────────
    console.print("\n[bold white]STEP 3 of 7 → Trip Type[/bold white]")
    trip_type = get_trip_type()
    
    # ── STEP 4: DATES ────────────────────────────────────────
    console.print("\n[bold white]STEP 4 of 7 → Travel Date(s)[/bold white]")
    
    depart_date = get_date_input("📅 Departure Date")
    
    return_date = None
    return_date_display = None
    
    if trip_type == "roundtrip":
        console.print("\n[dim]Now select your return date:[/dim]")
        min_return = datetime.strptime(depart_date, "%Y-%m-%d").date() + timedelta(days=1)
        return_date = get_date_input("📅 Return Date", min_date=min_return)
        return_date_display = datetime.strptime(
            return_date, "%Y-%m-%d"
        ).strftime("%A, %d %B %Y")
    
    # ── STEP 5: TIME FRAME ───────────────────────────────────
    console.print("\n[bold white]STEP 5 of 7 → Departure Time Preference[/bold white]")
    time_frame = get_time_frame()
    
    # ── STEP 6: PASSENGERS ───────────────────────────────────
    console.print("\n[bold white]STEP 6 of 7 → Passengers[/bold white]")
    passengers = get_passengers()
    
    # ── STEP 7: PREFERENCES ──────────────────────────────────
    console.print("\n[bold white]STEP 7 of 7 → Travel Class & Preferences[/bold white]")
    travel_class = get_travel_class()
    preferences = get_preferences()
    
    # ── BUILD FINAL PARAMS ───────────────────────────────────
    depart_date_display = datetime.strptime(
        depart_date, "%Y-%m-%d"
    ).strftime("%A, %d %B %Y")
    
    search_params = {
        # Airport Info
        "source":      source_airport,
        "destination": dest_airport,
        
        # Trip Details
        "trip_type":   trip_type,
        
        # Dates
        "depart_date":         depart_date,
        "depart_date_display": depart_date_display,
        "return_date":         return_date,
        "return_date_display": return_date_display,
        
        # Time Preference
        "time_frame":    time_frame,
        
        # Passengers
        "passengers":    passengers,
        
        # Class & Preferences
        "travel_class":  travel_class,
        "preferences":   preferences,
        
        # Metadata
        "search_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_passengers": passengers["adults"] + passengers["children"]
    }
    
    # Show Summary
    show_search_summary(search_params)
    
    # Confirm
    confirmed = Confirm.ask(
        "\n[bold yellow]✅ Start searching with these details?[/bold yellow]",
        default=True
    )
    
    if not confirmed:
        console.print("\n[yellow]Search cancelled. Restart to try again.[/yellow]")
        return None
    
    console.print("\n[bold green]🚀 Starting flight search...[/bold green]\n")
    
    return search_params