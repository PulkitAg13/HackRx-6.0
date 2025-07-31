import hashlib
from typing import Optional, List
from datetime import datetime
import re

def generate_unique_id():
    """Generate a unique ID based on current timestamp"""
    return hashlib.sha256(datetime.now().isoformat().encode()).hexdigest()[:16]

def validate_age(age: Optional[int]) -> bool:
    """Validate that age is within reasonable bounds"""
    if age is None:
        return True
    return 0 < age < 120

def format_currency(amount: Optional[float], currency: str = "INR") -> str:
    """Format currency amount with symbol"""
    if amount is None:
        return "N/A"
    
    currency_symbols = {
        "INR": "₹",
        "USD": "$",
        "EUR": "€",
        "GBP": "£"
    }
    
    symbol = currency_symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"

def extract_numbers(text: str) -> List[float]:
    """Extract all numbers from text"""
    numbers = re.findall(r"\d+\.?\d*", text)
    return [float(num) for num in numbers]