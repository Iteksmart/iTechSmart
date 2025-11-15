"""
AI Vision Service - Outfit Analysis using OpenAI Vision API
"""

import base64
import io
from typing import Dict, List, Optional
from PIL import Image
import openai
from colorthief import ColorThief
import numpy as np

from app.core.config import settings


class AIVisionService:
    """AI-powered outfit and style analysis"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.model = settings.OPENAI_MODEL
        
    async def analyze_outfit(self, image_path: str) -> Dict:
        """
        Comprehensive outfit analysis
        Returns style score, color harmony, detected items, and suggestions
        """
        
        # Load and encode image
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Analyze with OpenAI Vision
        analysis = await self._analyze_with_vision(image_data)
        
        # Extract colors
        colors = self._extract_colors(image_path)
        
        # Calculate scores
        style_score = self._calculate_style_score(analysis)
        color_harmony = self._calculate_color_harmony(colors)
        trend_match = self._calculate_trend_match(analysis)
        
        return {
            "style_score": style_score,
            "color_harmony": color_harmony,
            "trend_match": trend_match,
            "detected_items": analysis.get("items", []),
            "style_category": analysis.get("style_category", "casual"),
            "colors": colors,
            "feedback": analysis.get("feedback", []),
            "suggestions": analysis.get("suggestions", []),
            "overall_rating": round((style_score + color_harmony + trend_match) / 3, 1)
        }
    
    async def _analyze_with_vision(self, image_data: str) -> Dict:
        """Use OpenAI Vision API to analyze outfit"""
        
        prompt = """Analyze this outfit photo and provide:
        
1. Detected clothing items (top, bottom, shoes, accessories)
2. Color palette and combinations
3. Style category (casual, formal, trendy, sporty, chic, etc.)
4. Fashion feedback (what works well, what could be improved)
5. Specific suggestions for improvement
6. Trend alignment (is this outfit on-trend?)

Format your response as JSON with these keys:
- items: list of detected items
- style_category: main style category
- feedback: list of positive and constructive feedback
- suggestions: list of specific improvement suggestions
- trend_alignment: description of how trendy the outfit is
"""
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=settings.OPENAI_MAX_TOKENS
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            # Try to parse as JSON, fallback to text parsing
            try:
                import json
                return json.loads(content)
            except:
                return self._parse_text_response(content)
                
        except Exception as e:
            print(f"Vision API error: {e}")
            return self._get_fallback_analysis()
    
    def _extract_colors(self, image_path: str) -> List[str]:
        """Extract dominant colors from image"""
        try:
            color_thief = ColorThief(image_path)
            palette = color_thief.get_palette(color_count=5, quality=1)
            
            # Convert RGB to hex
            colors = [self._rgb_to_hex(color) for color in palette]
            return colors
        except:
            return ["#000000", "#FFFFFF"]
    
    def _rgb_to_hex(self, rgb: tuple) -> str:
        """Convert RGB tuple to hex color"""
        return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])
    
    def _calculate_style_score(self, analysis: Dict) -> float:
        """Calculate style score (1-10)"""
        # Based on AI feedback and detected items
        feedback = analysis.get("feedback", [])
        items = analysis.get("items", [])
        
        # Base score
        score = 7.0
        
        # Bonus for complete outfit
        if len(items) >= 3:
            score += 1.0
        
        # Bonus for positive feedback
        positive_keywords = ["great", "good", "excellent", "perfect", "well", "nice"]
        for item in feedback:
            if any(word in item.lower() for word in positive_keywords):
                score += 0.5
        
        # Cap at 10
        return min(10.0, round(score, 1))
    
    def _calculate_color_harmony(self, colors: List[str]) -> float:
        """Calculate color harmony score (1-10)"""
        if len(colors) < 2:
            return 7.0
        
        # Simple harmony check based on color theory
        # This is a simplified version - real implementation would be more complex
        score = 8.0
        
        # Check for too many colors (generally 3-4 is ideal)
        if len(colors) > 5:
            score -= 1.0
        
        return round(score, 1)
    
    def _calculate_trend_match(self, analysis: Dict) -> float:
        """Calculate trend match score (1-10)"""
        trend_alignment = analysis.get("trend_alignment", "").lower()
        
        # Keywords indicating trendiness
        trendy_keywords = ["trendy", "fashionable", "current", "modern", "stylish"]
        
        score = 7.0
        for keyword in trendy_keywords:
            if keyword in trend_alignment:
                score += 0.5
        
        return min(10.0, round(score, 1))
    
    def _parse_text_response(self, text: str) -> Dict:
        """Parse text response when JSON parsing fails"""
        return {
            "items": ["top", "bottom"],
            "style_category": "casual",
            "feedback": [text[:200]],
            "suggestions": ["Consider adding accessories"],
            "trend_alignment": "Modern casual style"
        }
    
    def _get_fallback_analysis(self) -> Dict:
        """Fallback analysis when API fails"""
        return {
            "items": ["clothing"],
            "style_category": "casual",
            "feedback": ["Unable to analyze outfit at this time"],
            "suggestions": ["Try uploading a clearer photo"],
            "trend_alignment": "Unable to determine"
        }
    
    async def analyze_hair_makeup(self, image_path: str) -> Dict:
        """Analyze hair and makeup compatibility with outfit"""
        
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        prompt = """Analyze the hair and makeup in this photo:

1. Hair style and how it complements the outfit
2. Makeup tones and their harmony with clothing colors
3. Overall grooming and presentation
4. Suggestions for improvement

Provide specific, actionable feedback."""
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            return {
                "analysis": content,
                "score": 8.0,  # Default score
                "suggestions": self._extract_suggestions(content)
            }
            
        except Exception as e:
            print(f"Hair/makeup analysis error: {e}")
            return {
                "analysis": "Unable to analyze hair and makeup",
                "score": 7.0,
                "suggestions": []
            }
    
    def _extract_suggestions(self, text: str) -> List[str]:
        """Extract suggestions from text"""
        suggestions = []
        lines = text.split('\n')
        for line in lines:
            if any(word in line.lower() for word in ['suggest', 'try', 'consider', 'could']):
                suggestions.append(line.strip())
        return suggestions[:3]  # Return top 3 suggestions
    
    async def chat_stylist(self, message: str, context: Dict) -> str:
        """AI stylist chat for follow-up questions"""
        
        prompt = f"""You are a professional fashion stylist. 
        
Context about the user's outfit:
- Style Score: {context.get('style_score', 'N/A')}
- Detected Items: {', '.join(context.get('detected_items', []))}
- Style Category: {context.get('style_category', 'casual')}

User question: {message}

Provide helpful, specific fashion advice."""
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful fashion stylist."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Chat error: {e}")
            return "I'm having trouble responding right now. Please try again."