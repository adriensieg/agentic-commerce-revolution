"""
Burger database
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

BURGERS: List[Dict[str, Any]] = [
    {
        "id": "classic-beef",
        "name": "Classic Beef Burger",
        "description": "Juicy beef patty with lettuce, tomato, onion, and our special sauce",
        "price": 8.99,
        "calories": 650,
        "ingredients": ["beef", "lettuce", "tomato", "onion", "sauce", "bun"],
        "thumbnail": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=300&h=200&fit=crop"
    },
    {
        "id": "chicken-deluxe",
        "name": "Chicken Deluxe",
        "description": "Grilled chicken breast with avocado, bacon, and ranch dressing",
        "price": 9.99,
        "calories": 580,
        "ingredients": ["chicken", "avocado", "bacon", "ranch", "lettuce", "bun"],
        "thumbnail": "https://images.unsplash.com/photo-1606755962773-d324e0a13086?w=300&h=200&fit=crop"
    },
    {
        "id": "veggie-supreme",
        "name": "Veggie Supreme",
        "description": "Plant-based patty with grilled vegetables and hummus",
        "price": 7.99,
        "calories": 420,
        "ingredients": ["veggie-patty", "grilled-vegetables", "hummus", "lettuce", "tomato", "bun"],
        "thumbnail": "https://images.unsplash.com/photo-1520072959219-c595dc870360?w=300&h=200&fit=crop"
    },
    {
        "id": "bacon-cheese",
        "name": "Bacon Cheeseburger",
        "description": "Double beef patties with crispy bacon and melted cheddar",
        "price": 11.99,
        "calories": 890,
        "ingredients": ["beef", "bacon", "cheese", "pickles", "onion", "bun"],
        "thumbnail": "https://images.unsplash.com/photo-1553979459-d2229ba7433b?w=300&h=200&fit=crop"
    },
    {
        "id": "spicy-chicken",
        "name": "Spicy Chicken Burger",
        "description": "Crispy fried chicken with jalapeños and spicy mayo",
        "price": 9.69,
        "calories": 720,
        "ingredients": ["chicken", "jalapeños", "spicy-mayo", "lettuce", "pickles", "bun"],
        "thumbnail": "https://images.unsplash.com/photo-1606755962773-d324e0a13086?w=300&h=200&fit=crop"
    },
    {
        "id": "mushroom-swiss",
        "name": "Mushroom Swiss Burger",
        "description": "Beef patty topped with sautéed mushrooms and Swiss cheese",
        "price": 10.49,
        "calories": 700,
        "ingredients": ["beef", "mushrooms", "swiss-cheese", "onion", "sauce", "bun"],
        "thumbnail": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=300&h=200&fit=crop"
    },
    {
        "id": "fish-burger",
        "name": "Fish Burger",
        "description": "Crispy fish fillet with tartar sauce and coleslaw",
        "price": 8.49,
        "calories": 540,
        "ingredients": ["fish", "tartar-sauce", "coleslaw", "lettuce", "bun"],
        "thumbnail": "https://images.unsplash.com/photo-1603360946369-dc9bb6258143?w=300&h=200&fit=crop"
    },
    {
        "id": "bbq-bacon",
        "name": "BBQ Bacon Burger",
        "description": "Beef patty with BBQ sauce, crispy bacon, and onion rings",
        "price": 10.99,
        "calories": 820,
        "ingredients": ["beef", "bacon", "bbq-sauce", "onion-rings", "cheese", "bun"],
        "thumbnail": "https://images.unsplash.com/photo-1550547660-d9450f859349?w=300&h=200&fit=crop"
    }
]

logger.info(f"Loaded {len(BURGERS)} burgers into database")
