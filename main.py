# ============================================================
# main.py - Updated with complete user input
# ============================================================

import sys
import re
from rich.console import Console
from user_input.input_handler import collect_all_inputs
from scrapers.google_flights import GoogleFlightsScraper
from scrapers.ixigo_scraper import IxigoScraper
from scrapers.makemytrip import MakeMyTripScraper
from llm.analyzer import FlightAnalyzer
from utils.helpers import format_date_display
import pandas as pd
import json
from datetime import datetime
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Confirm

console = Console()

def run_scrapers(search_params: dict) -> dict:
    """
    Run scrapers for one-way or round-trip
    Returns dict with outbound and return flights
    """
    
    from_code  = search_params["source"]["code"]
    to_code    = search_params["destination"]["code"]
    depart_date = search_params["depart_date"]
    return_date = search_params.get("return_date")
    trip_type   = search_params["trip_type"]
    
    scrapers = [
        GoogleFlightsScraper(),
        IxigoScraper(),
        MakeMyTripScraper(),
    ]
    
    results = {
        "outbound": [],
        "return":   []
    }
    
    # ── OUTBOUND FLIGHTS ─────────────────────────────────────
    console.print(
        f"\n[bold cyan]🛫 Searching OUTBOUND flights: "
        f"{from_code} → {to_code} on {depart_date}[/bold cyan]\n"
    )
    
    for scraper in scrapers:
        try:
            with console.status(f"[cyan]Searching {scraper.source}...[/cyan]"):
                flights = scraper.scrape(from_code, to_code, depart_date)
            
            if flights:
                results["outbound"].extend(flights)
                console.print(
                    f"[green]✅ {scraper.source}: "
                    f"Found {len(flights)} outbound flights[/green]"
                )
            else:
                console.print(f"[yellow]⚠️ {scraper.source}: No outbound results[/yellow]")
                
        except Exception as e:
            console.print(f"[red]❌ {scraper.source}: {str(e)}[/red]")
    
    # ── RETURN FLIGHTS (if round-trip) ───────────────────────
    if trip_type == "roundtrip" and return_date:
        console.print(
            f"\n[bold cyan]🛬 Searching RETURN flights: "
            f"{to_code} → {from_code} on {return_date}[/bold cyan]\n"
        )
        
        for scraper in scrapers:
            try:
                with console.status(f"[cyan]Searching {scraper.source} (return)...[/cyan]"):
                    flights = scraper.scrape(to_code, from_code, return_date)
                
                if flights:
                    results["return"].extend(flights)
                    console.print(
                        f"[green]✅ {scraper.source}: "
                        f"Found {len(flights)} return flights[/green]"
                    )
                else:
                    console.print(
                        f"[yellow]⚠️ {scraper.source}: No return results[/yellow]"
                    )
                    
            except Exception as e:
                console.print(f"[red]❌ {scraper.source} (return): {str(e)}[/red]")
    
    return results

def filter_by_time(flights: list, time_frame: dict) -> list:
    """Filter flights by preferred time frame"""
    
    if time_frame["start_hour"] == 0 and time_frame["end_hour"] == 24:
        return flights  # No filter - any time
    
    filtered = []
    for flight in flights:
        dep_time = flight.get("departure_time", "")
        try:
            # Parse time like "06:30" or "6:30 AM"
            if "AM" in dep_time or "PM" in dep_time:
                hour = int(
                    datetime.strptime(dep_time.strip(), "%I:%M %p").strftime("%H")
                )
            else:
                hour = int(dep_time.split(":")[0])
            
            if time_frame["start_hour"] <= hour < time_frame["end_hour"]:
                filtered.append(flight)
        except:
            filtered.append(flight)  # Include if can't parse time
    
    return filtered if filtered else flights  # Return all if none match

def filter_flights(flights: list, search_params: dict) -> list:
    """Apply all filters based on preferences"""
    
    filtered = flights.copy()
    prefs = search_params["preferences"]
    
    # Filter by time frame
    filtered = filter_by_time(filtered, search_params["time_frame"])
    
    # Filter non-stop only
    if prefs.get("nonstop_only"):
        nonstop = [
            f for f in filtered
            if "non-stop" in str(f.get("stops", "")).lower()
            or "0" in str(f.get("stops", ""))
            or "direct" in str(f.get("stops", "")).lower()
        ]
        filtered = nonstop if nonstop else filtered
    
    # Filter by max budget
    if prefs.get("max_budget"):
        budget_filtered = [
            f for f in filtered
            if f.get("price", 999999) <= prefs["max_budget"]
        ]
        filtered = budget_filtered if budget_filtered else filtered
    
    # Filter by preferred airline
    if prefs.get("preferred_airline"):
        airline_filtered = [
            f for f in filtered
            if prefs["preferred_airline"].lower() in 
               str(f.get("airline", "")).lower()
        ]
        filtered = airline_filtered if airline_filtered else filtered
    
    return filtered

def display_flight_results(
    flight_results: dict,
    search_params: dict
):
    """Display outbound and return flights"""
    
    src  = search_params["source"]["city"]
    dest = search_params["destination"]["city"]
    
    # Outbound Flights Table
    outbound = flight_results.get("outbound", [])
    filtered_out = filter_flights(outbound, search_params)
    
    if filtered_out:
        sorted_out = sorted(
            filtered_out,
            key=lambda x: x.get("price", 999999)
        )
        
        console.print(
            f"\n[bold]✈️  OUTBOUND FLIGHTS: "
            f"{src} → {dest} "
            f"({search_params['depart_date_display']})[/bold]\n"
        )
        
        _display_table(sorted_out, "OUTBOUND")
    
    # Return Flights Table (if round-trip)
    if search_params["trip_type"] == "roundtrip":
        return_flights = flight_results.get("return", [])
        filtered_ret   = filter_flights(return_flights, search_params)
        
        if filtered_ret:
            sorted_ret = sorted(
                filtered_ret,
                key=lambda x: x.get("price", 999999)
            )
            
            console.print(
                f"\n[bold]🔄 RETURN FLIGHTS: "
                f"{dest} → {src} "
                f"({search_params.get('return_date_display', 'N/A')})[/bold]\n"
            )
            
            _display_table(sorted_ret, "RETURN")
            
            # Show combined round-trip cost
            if sorted_out and sorted_ret:
                cheapest_out = sorted_out[0].get("price", 0)
                cheapest_ret = sorted_ret[0].get("price", 0)
                total = cheapest_out + cheapest_ret
                
                console.print(Panel(
                    f"🛫 Cheapest Outbound: [bold green]₹{cheapest_out:,}[/bold green]\n"
                    f"🛬 Cheapest Return:   [bold green]₹{cheapest_ret:,}[/bold green]\n"
                    f"─────────────────────────────\n"
                    f"💰 Total Round Trip:  "
                    f"[bold yellow]₹{total:,}[/bold yellow] per person",
                    title="💹 ROUND TRIP COST SUMMARY",
                    border_style="bold green"
                ))

def _display_table(flights: list, flight_type: str):
    """Helper to display flight table"""
    
    table = Table(
        show_header=True,
        header_style="bold magenta",
        border_style="blue",
        show_lines=True
    )
    
    table.add_column("#",        style="dim",         width=3)
    table.add_column("Platform", style="cyan",        width=14)
    table.add_column("Airline",  style="white",       width=14)
    table.add_column("Price ₹",  style="bold green",  width=10, justify="right")
    table.add_column("Departs",  style="yellow",      width=8)
    table.add_column("Arrives",  style="yellow",      width=8)
    table.add_column("Duration", style="white",       width=9)
    table.add_column("Stops",    style="white",       width=12)
    
    for i, f in enumerate(flights[:15], 1):
        price = f.get("price", 0)
        price_str = f"₹{price:,}" if price < 999999 else "N/A"
        row_style = "bold green" if i == 1 else ""
        
        table.add_row(
            str(i),
            f.get("source",         "N/A"),
            f.get("airline",        "N/A"),
            price_str,
            f.get("departure_time", "N/A"),
            f.get("arrival_time",   "N/A"),
            f.get("duration",       "N/A"),
            f.get("stops",          "N/A"),
            style=row_style
        )
    
    console.print(table)

def _format_money(value) -> str:
    """
    Safely format a price as ₹-prefixed with thousands separators.

    The LLM (and the rule-based fallback) may return prices as ints, numeric
    strings like "4500"/"₹4,500", or "N/A". Coerce to int when possible so the
    display never crashes on `:,` formatting of a non-numeric value.
    """
    if value is None:
        return "N/A"
    if isinstance(value, (int, float)):
        return f"₹{int(value):,}"
    # String: strip currency symbols/commas and parse the digits.
    digits = re.sub(r"[^\d]", "", str(value))
    if digits:
        return f"₹{int(digits):,}"
    return "N/A"

def display_ai_recommendation(analysis: dict):
    """Display LLM analysis results as rich panels"""

    if not analysis:
        return

    console.print("\n" + "=" * 60)
    console.print("[bold magenta]🤖 AI FLIGHT ANALYSIS & RECOMMENDATIONS[/bold magenta]")
    console.print("=" * 60 + "\n")

    # Best Overall
    if analysis.get("best_overall"):
        best = analysis["best_overall"]
        console.print(Panel(
            f"✈️ Airline: [bold]{best.get('airline', 'N/A')}[/bold]\n"
            f"💰 Price: [bold green]{_format_money(best.get('price'))}[/bold green]\n"
            f"🌐 Book on: [bold cyan]{best.get('source', 'N/A')}[/bold cyan]\n"
            f"🕐 Departure: {best.get('departure', 'N/A')}\n"
            f"🕐 Arrival: {best.get('arrival', 'N/A')}\n"
            f"⏱️ Duration: {best.get('duration', 'N/A')}\n"
            f"🛑 Stops: {best.get('stops', 'N/A')}\n\n"
            f"[italic]{best.get('reason', '')}[/italic]",
            title="🏆 BEST OVERALL RECOMMENDATION",
            border_style="bold green"
        ))

    # Cheapest Option
    if analysis.get("cheapest"):
        cheap = analysis["cheapest"]
        console.print(Panel(
            f"✈️ Airline: [bold]{cheap.get('airline', 'N/A')}[/bold]\n"
            f"💰 Price: [bold green]{_format_money(cheap.get('price'))}[/bold green]\n"
            f"🌐 Book on: [bold cyan]{cheap.get('source', 'N/A')}[/bold cyan]\n"
            f"[italic]{cheap.get('reason', '')}[/italic]",
            title="💸 CHEAPEST OPTION",
            border_style="yellow"
        ))

    # Price Insights
    if analysis.get("price_insights"):
        insights = analysis["price_insights"]
        console.print(Panel(
            f"📉 Lowest Price: [bold green]{_format_money(insights.get('lowest_price'))}[/bold green]\n"
            f"📈 Highest Price: [bold red]{_format_money(insights.get('highest_price'))}[/bold red]\n"
            f"📊 Average Price: [bold yellow]{_format_money(insights.get('average_price'))}[/bold yellow]\n"
            f"🏆 Best Platform: [bold cyan]{insights.get('best_platform', 'N/A')}[/bold cyan]\n"
            f"📝 {insights.get('price_range', '')}",
            title="💹 PRICE INSIGHTS",
            border_style="cyan"
        ))

    # Money Saving Tips
    if analysis.get("savings_tips"):
        tips_text = "\n".join([f"  ✅ {tip}" for tip in analysis["savings_tips"]])
        console.print(Panel(
            tips_text,
            title="💡 MONEY SAVING TIPS",
            border_style="blue"
        ))

    # Booking Advice
    if analysis.get("booking_advice"):
        console.print(Panel(
            analysis["booking_advice"],
            title="📝 BOOKING ADVICE",
            border_style="magenta"
        ))

    # Overall Summary
    if analysis.get("overall_summary"):
        console.print(Panel(
            f"[bold]{analysis['overall_summary']}[/bold]",
            title="📊 SUMMARY",
            border_style="white"
        ))

def save_results(
    flight_results: dict,
    analysis: dict,
    search_params: dict
):
    """Save all results"""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    src  = search_params["source"]["code"]
    dest = search_params["destination"]["code"]
    
    # CSV for outbound
    if flight_results.get("outbound"):
        df = pd.DataFrame(flight_results["outbound"])
        fname = f"outbound_{src}_{dest}_{ts}.csv"
        df.to_csv(fname, index=False)
        console.print(f"[green]💾 Saved: {fname}[/green]")
    
    # CSV for return
    if flight_results.get("return"):
        df = pd.DataFrame(flight_results["return"])
        fname = f"return_{dest}_{src}_{ts}.csv"
        df.to_csv(fname, index=False)
        console.print(f"[green]💾 Saved: {fname}[/green]")
    
    # JSON for complete results
    fname = f"flight_search_{src}_{dest}_{ts}.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(
            {
                "search_params": {
                    k: v for k, v in search_params.items()
                    if isinstance(v, (str, int, float, bool, dict, list))
                },
                "results":  flight_results,
                "analysis": analysis
            },
            f, indent=2, ensure_ascii=False
        )
    console.print(f"[green]💾 Saved: {fname}[/green]")

def main():
    try:
        # ── COLLECT ALL USER INPUTS ──────────────────────────
        search_params = collect_all_inputs()
        
        if not search_params:
            sys.exit(0)
        
        # ── SCRAPE FLIGHTS ───────────────────────────────────
        flight_results = run_scrapers(search_params)
        
        total_found = (
            len(flight_results.get("outbound", [])) +
            len(flight_results.get("return",   []))
        )
        
        if total_found == 0:
            console.print("\n[red]❌ No flights found from any source.[/red]")
            console.print("[yellow]Try different dates or check internet connection.[/yellow]")
            sys.exit(1)
        
        # ── DISPLAY ALL RESULTS ──────────────────────────────
        display_flight_results(flight_results, search_params)
        
        # ── AI ANALYSIS ──────────────────────────────────────
        console.print("\n[bold cyan]🤖 Running AI Analysis...[/bold cyan]\n")
        
        analyzer = FlightAnalyzer()
        
        # Analyze outbound
        outbound_analysis = analyzer.analyze_flights(
            flight_results.get("outbound", []),
            search_params["source"]["city"],
            search_params["destination"]["city"],
            search_params["depart_date"],
            search_params["preferences"]
        )
        
        # Analyze return (if round-trip)
        return_analysis = None
        if search_params["trip_type"] == "roundtrip":
            return_analysis = analyzer.analyze_flights(
                flight_results.get("return", []),
                search_params["destination"]["city"],
                search_params["source"]["city"],
                search_params.get("return_date", ""),
                search_params["preferences"]
            )
        
        # Display analysis results
        console.print("\n[bold]🤖 OUTBOUND FLIGHT ANALYSIS:[/bold]")
        display_ai_recommendation(outbound_analysis)
        
        if return_analysis:
            console.print("\n[bold]🤖 RETURN FLIGHT ANALYSIS:[/bold]")
            display_ai_recommendation(return_analysis)
        
        # ── SAVE RESULTS ─────────────────────────────────────
        if Confirm.ask("\n[cyan]💾 Save results to files?[/cyan]", default=True):
            save_results(
                flight_results,
                {
                    "outbound": outbound_analysis,
                    "return":   return_analysis
                },
                search_params
            )
        
        console.print("\n[bold green]✅ Done! Happy flying! 🛫[/bold green]\n")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Search cancelled.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        raise

if __name__ == "__main__":
    main()