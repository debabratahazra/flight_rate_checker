import json
import os
import config
from rich.console import Console

# Read config defensively: config.py may not define every LLM name (e.g. when
# only OpenAI is configured). Missing names fall back to safe defaults so the
# analyzer can still initialize and degrade to rule-based analysis.
LLM_PROVIDER = getattr(config, "LLM_PROVIDER", "openai")
OPENAI_API_KEY = getattr(config, "OPENAI_API_KEY", "")
GEMINI_API_KEY = getattr(config, "GEMINI_API_KEY", "")
LLM_MODEL_OPENAI = getattr(config, "LLM_MODEL_OPENAI", "gpt-4o-mini")
LLM_MODEL_GEMINI = getattr(config, "LLM_MODEL_GEMINI", "gemini-1.5-flash")

console = Console()

class FlightAnalyzer:
    """LLM-powered flight analyzer to find best deals"""
    
    def __init__(self):
        self.provider = LLM_PROVIDER
        self._setup_llm()
    
    def _setup_llm(self):
        """Initialize LLM based on provider"""
        if self.provider == "openai":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=OPENAI_API_KEY)
                console.print("[green]✅ OpenAI LLM initialized[/green]")
            except Exception as e:
                console.print(f"[red]OpenAI setup error: {e}[/red]")
                
        elif self.provider == "gemini":
            try:
                import google.generativeai as genai
                genai.configure(api_key=GEMINI_API_KEY)
                self.client = genai.GenerativeModel(LLM_MODEL_GEMINI)
                console.print("[green]✅ Gemini LLM initialized[/green]")
            except Exception as e:
                console.print(f"[red]Gemini setup error: {e}[/red]")
    
    def analyze_flights(
        self, 
        flights: list, 
        from_city: str, 
        to_city: str, 
        date: str,
        preferences: dict = None
    ) -> dict:
        """
        Use LLM to analyze all flights and recommend best option
        
        Args:
            flights: List of all scraped flight data
            from_city: Departure city
            to_city: Destination city
            date: Travel date
            preferences: User preferences (priority: price/time/comfort)
        
        Returns:
            Dict with analysis and recommendations
        """
        
        if not flights:
            return {
                "status": "no_flights",
                "message": "No flights found",
                "recommendation": None,
                "analysis": None
            }
        
        # Prepare flight data for LLM
        flight_summary = self._prepare_flight_summary(flights)
        
        # Build prompt
        prompt = self._build_analysis_prompt(
            flight_summary, 
            from_city, 
            to_city, 
            date, 
            preferences
        )
        
        # Get LLM response
        console.print("[cyan]🤖 Analyzing flights with AI...[/cyan]")
        
        try:
            if self.provider == "openai":
                response = self._query_openai(prompt)
            elif self.provider == "gemini":
                response = self._query_gemini(prompt)
            else:
                response = self._fallback_analysis(flights)
            
            return response
            
        except Exception as e:
            console.print(f"[red]LLM Analysis error: {e}[/red]")
            return self._fallback_analysis(flights)
    
    def _prepare_flight_summary(self, flights: list) -> str:
        """Convert flight data to readable summary for LLM"""
        summary = []
        
        for i, flight in enumerate(flights, 1):
            summary.append(
                f"Flight {i}:\n"
                f"  Source: {flight.get('source', 'N/A')}\n"
                f"  Airline: {flight.get('airline', 'N/A')}\n"
                f"  Price: ₹{flight.get('price', 'N/A')}\n"
                f"  Departure: {flight.get('departure_time', 'N/A')}\n"
                f"  Arrival: {flight.get('arrival_time', 'N/A')}\n"
                f"  Duration: {flight.get('duration', 'N/A')}\n"
                f"  Stops: {flight.get('stops', 'N/A')}\n"
            )
        
        return "\n".join(summary)
    
    def _build_analysis_prompt(
        self, 
        flight_summary: str, 
        from_city: str, 
        to_city: str, 
        date: str,
        preferences: dict
    ) -> str:
        """Build detailed prompt for LLM"""
        
        pref_text = ""
        if preferences:
            if preferences.get("priority") == "price":
                pref_text = "User's priority is LOWEST PRICE."
            elif preferences.get("priority") == "time":
                pref_text = "User's priority is FASTEST/SHORTEST flight time."
            elif preferences.get("priority") == "comfort":
                pref_text = "User's priority is COMFORT (direct flights preferred)."
            
            if preferences.get("max_budget"):
                pref_text += f" Maximum budget is ₹{preferences['max_budget']}."
            
            if preferences.get("preferred_time"):
                pref_text += f" Preferred departure time: {preferences['preferred_time']}."
        
        prompt = f"""
You are an expert flight advisor helping Indian travelers find the best domestic flight deals.

SEARCH DETAILS:
- From: {from_city}
- To: {to_city}  
- Date: {date}
- {pref_text if pref_text else "No specific preferences mentioned."}

AVAILABLE FLIGHTS DATA (scraped from multiple booking websites):
{flight_summary}

Please analyze all the above flights and provide:

1. **BEST OVERALL RECOMMENDATION** - The single best flight considering price, timing, and value
2. **CHEAPEST OPTION** - The lowest priced flight available
3. **BEST VALUE** - Best balance of price and convenience (non-stop, good timing)
4. **PRICE COMPARISON** - How prices compare across different booking platforms
5. **MONEY SAVING TIPS** - Specific tips for this route and date
6. **BOOKING ADVICE** - Which website to book from and why

Please provide your response in the following JSON format:
{{
    "best_overall": {{
        "flight_number": <number from list>,
        "airline": "<airline name>",
        "price": <price in INR>,
        "source": "<booking website>",
        "departure": "<time>",
        "arrival": "<time>",
        "duration": "<duration>",
        "stops": "<stops info>",
        "reason": "<why this is best overall>"
    }},
    "cheapest": {{
        "flight_number": <number>,
        "airline": "<airline name>",
        "price": <price>,
        "source": "<booking website>",
        "reason": "<why cheapest>"
    }},
    "best_value": {{
        "flight_number": <number>,
        "airline": "<airline name>",
        "price": <price>,
        "source": "<booking website>",
        "reason": "<why best value>"
    }},
    "price_insights": {{
        "lowest_price": <number>,
        "highest_price": <number>,
        "average_price": <number>,
        "price_range": "<range description>",
        "best_platform": "<which platform has cheapest prices>"
    }},
    "savings_tips": [
        "<tip 1>",
        "<tip 2>",
        "<tip 3>"
    ],
    "booking_advice": "<detailed booking advice>",
    "overall_summary": "<2-3 line summary of findings>"
}}
"""
        return prompt
    
    def _query_openai(self, prompt: str) -> dict:
        """Query OpenAI GPT"""
        response = self.client.chat.completions.create(
            model=LLM_MODEL_OPENAI,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert travel advisor. Always respond with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
    
    def _query_gemini(self, prompt: str) -> dict:
        """Query Google Gemini"""
        
        # Add JSON instruction for Gemini
        full_prompt = prompt + "\n\nIMPORTANT: Respond ONLY with valid JSON, no markdown, no extra text."
        
        response = self.client.generate_content(
            full_prompt,
            generation_config={
                "temperature": 0.3,
                "top_p": 0.8,
            }
        )
        
        content = response.text
        
        # Clean JSON response
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise
    
    def _fallback_analysis(self, flights: list) -> dict:
        """Fallback analysis without LLM (rule-based)"""
        
        if not flights:
            return {"status": "no_flights"}
        
        # Sort by price
        valid_flights = [f for f in flights if f.get('price', 999999) < 999999]
        
        if not valid_flights:
            valid_flights = flights
        
        sorted_by_price = sorted(valid_flights, key=lambda x: x.get('price', 999999))
        cheapest = sorted_by_price[0]
        
        # Find non-stop flights
        nonstop = [f for f in valid_flights if 'non-stop' in str(f.get('stops', '')).lower() 
                   or '0' in str(f.get('stops', ''))]
        
        best_value = nonstop[0] if nonstop else cheapest
        
        prices = [f.get('price', 0) for f in valid_flights if f.get('price', 0) > 0]
        
        return {
            "best_overall": {
                "airline": best_value.get('airline', 'N/A'),
                "price": best_value.get('price', 'N/A'),
                "source": best_value.get('source', 'N/A'),
                "departure": best_value.get('departure_time', 'N/A'),
                "reason": "Best combination of price and convenience"
            },
            "cheapest": {
                "airline": cheapest.get('airline', 'N/A'),
                "price": cheapest.get('price', 'N/A'),
                "source": cheapest.get('source', 'N/A'),
                "reason": "Lowest price found"
            },
            "price_insights": {
                "lowest_price": min(prices) if prices else 0,
                "highest_price": max(prices) if prices else 0,
                "average_price": sum(prices) // len(prices) if prices else 0,
            },
            "savings_tips": [
                "Book in advance for better prices",
                "Consider flying on weekdays",
                "Check airline websites directly for exclusive deals"
            ],
            "overall_summary": f"Found {len(valid_flights)} flights. Cheapest is ₹{cheapest.get('price')} on {cheapest.get('source')}"
        }