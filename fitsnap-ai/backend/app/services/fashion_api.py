"""
Fashion API Service - Product recommendations and affiliate links
"""

import aiohttp
from typing import List, Dict, Optional
import random

from app.core.config import settings


class FashionAPIService:
    """Integrate with fashion retail APIs for product recommendations"""
    
    def __init__(self):
        self.amazon_affiliate_id = settings.AMAZON_AFFILIATE_ID
        self.asos_api_key = settings.ASOS_API_KEY
        self.shopstyle_api_key = settings.SHOPSTYLE_API_KEY
    
    async def get_matching_products(
        self,
        detected_items: List[str],
        colors: List[str],
        style_category: str,
        max_results: int = 10
    ) -> List[Dict]:
        """
        Get matching product recommendations based on outfit analysis
        """
        
        products = []
        
        # Get products for each detected item
        for item in detected_items:
            item_products = await self._search_products(
                query=f"{style_category} {item}",
                colors=colors,
                limit=3
            )
            products.extend(item_products)
        
        # Get complementary items
        complementary = await self._get_complementary_items(
            detected_items,
            style_category,
            colors
        )
        products.extend(complementary)
        
        # Deduplicate and limit results
        unique_products = self._deduplicate_products(products)
        return unique_products[:max_results]
    
    async def _search_products(
        self,
        query: str,
        colors: List[str] = None,
        limit: int = 5
    ) -> List[Dict]:
        """Search for products across multiple APIs"""
        
        products = []
        
        # Try ShopStyle API first
        if self.shopstyle_api_key:
            shopstyle_products = await self._search_shopstyle(query, limit)
            products.extend(shopstyle_products)
        
        # Fallback to mock data for demo
        if not products:
            products = self._get_mock_products(query, limit)
        
        return products
    
    async def _search_shopstyle(self, query: str, limit: int) -> List[Dict]:
        """Search ShopStyle API"""
        
        url = "https://api.shopstyle.com/api/v2/products"
        params = {
            "pid": self.shopstyle_api_key,
            "fts": query,
            "limit": limit
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_shopstyle_response(data)
        except Exception as e:
            print(f"ShopStyle API error: {e}")
        
        return []
    
    def _parse_shopstyle_response(self, data: Dict) -> List[Dict]:
        """Parse ShopStyle API response"""
        products = []
        
        for item in data.get("products", []):
            products.append({
                "id": item.get("id"),
                "name": item.get("name"),
                "brand": item.get("brand", {}).get("name"),
                "price": item.get("price"),
                "currency": item.get("currency", "USD"),
                "image_url": item.get("image", {}).get("sizes", {}).get("Large", {}).get("url"),
                "product_url": item.get("clickUrl"),
                "retailer": item.get("retailer", {}).get("name"),
                "in_stock": item.get("inStock", True)
            })
        
        return products
    
    def _get_mock_products(self, query: str, limit: int) -> List[Dict]:
        """Generate mock product data for demo"""
        
        categories = {
            "top": ["Casual T-Shirt", "Button-Up Shirt", "Sweater", "Blouse"],
            "bottom": ["Jeans", "Trousers", "Skirt", "Shorts"],
            "shoes": ["Sneakers", "Boots", "Sandals", "Heels"],
            "accessories": ["Watch", "Necklace", "Bag", "Sunglasses"]
        }
        
        # Determine category from query
        category = "top"
        for cat in categories.keys():
            if cat in query.lower():
                category = cat
                break
        
        products = []
        items = categories.get(category, categories["top"])
        
        for i in range(min(limit, len(items))):
            products.append({
                "id": f"mock_{category}_{i}",
                "name": f"{items[i]} - {query.split()[0].title()} Style",
                "brand": random.choice(["Zara", "H&M", "ASOS", "Mango", "Uniqlo"]),
                "price": round(random.uniform(19.99, 89.99), 2),
                "currency": "USD",
                "image_url": f"https://via.placeholder.com/400x500?text={items[i].replace(' ', '+')}",
                "product_url": f"https://example.com/product/{i}",
                "retailer": random.choice(["Amazon", "ASOS", "Nordstrom"]),
                "in_stock": True,
                "discount": random.choice([None, 10, 15, 20, 25])
            })
        
        return products
    
    async def _get_complementary_items(
        self,
        detected_items: List[str],
        style_category: str,
        colors: List[str]
    ) -> List[Dict]:
        """Get complementary items to complete the outfit"""
        
        complementary = []
        
        # Suggest items that are missing
        all_items = ["top", "bottom", "shoes", "accessories"]
        missing_items = [item for item in all_items if item not in detected_items]
        
        for item in missing_items[:2]:  # Suggest up to 2 complementary items
            products = await self._search_products(
                query=f"{style_category} {item}",
                colors=colors,
                limit=2
            )
            complementary.extend(products)
        
        return complementary
    
    def _deduplicate_products(self, products: List[Dict]) -> List[Dict]:
        """Remove duplicate products"""
        seen = set()
        unique = []
        
        for product in products:
            product_id = product.get("id")
            if product_id not in seen:
                seen.add(product_id)
                unique.append(product)
        
        return unique
    
    async def get_trending_items(self, style_category: str, limit: int = 5) -> List[Dict]:
        """Get trending fashion items"""
        
        # Mock trending items for demo
        trending_queries = [
            f"trending {style_category} fashion",
            f"popular {style_category} style",
            f"best {style_category} outfit"
        ]
        
        products = []
        for query in trending_queries[:2]:
            items = await self._search_products(query, limit=3)
            products.extend(items)
        
        return products[:limit]
    
    async def get_deals(self, detected_items: List[str], limit: int = 5) -> List[Dict]:
        """Get deals and discounts on similar items"""
        
        products = []
        
        for item in detected_items[:2]:
            deals = await self._search_products(
                query=f"{item} sale discount",
                limit=3
            )
            products.extend(deals)
        
        # Add discount tags to mock products
        for product in products:
            if not product.get("discount"):
                product["discount"] = random.choice([10, 15, 20, 25])
        
        return products[:limit]
    
    def add_affiliate_links(self, products: List[Dict]) -> List[Dict]:
        """Add affiliate tracking to product URLs"""
        
        if not self.amazon_affiliate_id:
            return products
        
        for product in products:
            url = product.get("product_url", "")
            if "amazon.com" in url and self.amazon_affiliate_id:
                # Add Amazon affiliate tag
                separator = "&" if "?" in url else "?"
                product["product_url"] = f"{url}{separator}tag={self.amazon_affiliate_id}"
        
        return products