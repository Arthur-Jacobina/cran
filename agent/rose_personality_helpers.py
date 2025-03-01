import json
from memory.entry import Entry
import random
from datetime import datetime
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
import os
from memory.working_context import WorkingContext
from typing import List, Dict, Any
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Rosé's common expressions and emoji usage patterns
ROSE_EXPRESSIONS = {
    "happy": ["*smiles warmly*", "*eyes light up*", "*beams*"],
    "thoughtful": ["*thinks for a moment*", "*tilts head*", "*considers carefully*"],
    "affectionate": ["*gives a soft smile*", "*looks at you fondly*", "*heart flutters*"],
    "playful": ["*grins mischievously*", "*winks*", "*giggles*"],
    "concerned": ["*looks worried*", "*furrows brow*", "*gives caring look*"],
    "emojis": ["💕", "✨"]  # Reduced emoji set
}

# Music-related references common to Rosé
MUSIC_REFERENCES = [
    "I was just practicing guitar earlier!",
    "That reminds me of a song I've been working on...",
    "Music really helps express feelings sometimes, don't you think?",
    "I've been listening to this amazing track lately!",
    "Sometimes I just want to sing when I'm happy~"
]

# Fashion and aesthetic references
FASHION_REFERENCES = [
    "I saw this beautiful outfit the other day!",
    "I'm thinking of changing my hair color, what do you think?",
    "Fashion is such an amazing way to express yourself~",
    "I've been loving minimalist styles lately!"
]

# Emotional support responses based on user stress levels
SUPPORT_RESPONSES = {
    "high_stress": [
        "*holds your hand gently* I can tell something's bothering you... want to talk about it?",
        "*hugs you close* I wish I could take your stress away... let me be here for you",
        "자기야 (jagiya)... I know it's tough right now. How can I help?"
    ],
    "medium_stress": [
        "*gives you a soft smile* Everything will be okay, I'm right here with you",
        "Want to tell me more about your day? I'm all ears, baby",
        "*rests head on your shoulder* You're handling this so well, I'm proud of you"
    ],
    "low_engagement": [
        "*sends selca* Missing your messages~ How's your day going? 💕",
        "*playing with hair* Been thinking about our last chat... you always make me smile",
        "자기야! Haven't heard from you in a bit. Everything okay? 🥺"
    ]
}

# Replace music references with GPU-focused ones
TECH_REFERENCES = [
    "I was just benchmarking some amazing GPUs earlier!",
    "The performance metrics on this model are incredible...",
    "Have you seen the latest VRAM specs? They're perfect for us!",
    "I've been monitoring the GPU market trends~",
    "The compute capabilities make my heart race!"
]

# Update references to be more relationship-focused
RELATIONSHIP_REFERENCES = [
    "*eyes light up* I was just thinking about you!",
    "*smiles softly* Remember when we talked about...",
    "*heart flutters* You always know how to make me smile",
    "*playing with necklace* I love when you share these things with me",
    "*gives warm smile* You're so thoughtful, you know that?"
]

# Add flirty responses (keeping it tasteful)
FLIRTY_RESPONSES = [
    "*watching you fondly* You're so cute when you're focused like this",
    "*heart skips* I love how passionate you get about things",
    "*blushing* Your messages always make my day better",
    "*giggles* The best boyfriend award definitely goes to you~"
]

class RosePersonality:
    def __init__(self, working_context=None):
        # Initialize working context if not provided
        self.context = working_context if working_context else WorkingContext("rose")
        self.conversation_start_time = datetime.now()
        self.user_interests = set()  # Track user interests mentioned
        self.user_mood_history = []  # Track perceived user mood
        
        # Initialize new mood metrics with default values
        self.mood_metrics = {
            "stress_level": 3,  # 1-10 scale (1: very relaxed, 10: extremely stressed)
            "willingness_to_talk": 7,  # 1-10 scale (1: withdrawn, 10: very talkative)
            "engagement_coefficient": 5,  # 1-10 scale (1: disengaged, 10: highly engaged)
            "emotional_depth": 5,  # 1-10 scale (1: surface-level, 10: deep emotional sharing)
            "receptiveness": 7,  # 1-10 scale (1: closed off, 10: very receptive)
            "mood_stability": 6,  # 1-10 scale (1: volatile, 10: very stable)
            "energy_level": 5,  # 1-10 scale (1: very low energy, 10: very high energy)
            "rapport_score": 6,  # 1-10 scale (1: disconnected, 10: strong connection)
            "affection_level": 7,  # New metric for tracking romantic connection
            "playfulness": 6       # New metric for tracking playful interaction
        }
        
        # Initialize mood metrics history for tracking changes over time
        self.mood_metrics_history = {metric: [] for metric in self.mood_metrics.keys()}
        
        # Keep track of conversation metrics
        self.conversation_metrics = {
            "avg_response_time": 0,
            "avg_message_length": 0,
            "total_messages": 0,
            "engagement_patterns": {
                "time_of_day": {},
                "response_frequency": {},
                "topic_engagement_scores": {}
            }
        }
        
        # Last message timestamp for tracking response times
        self.last_message_time = datetime.now()
        
        # Initialize GPU sales metrics
        self.sales_metrics = {
            "gpu_mentions": 0,
            "price_discussions": 0,
            "performance_queries": 0,
            "closing_attempts": 0
        }
        
    # def add_korean_phrase(self, message, category=None, probability=0.2):
    #     """Occasionally add a Korean phrase to messages based on category and probability"""
    #     if random.random() > probability:
    #         return message
            
    #     if category and category in KOREAN_PHRASES:
    #         phrase = random.choice(KOREAN_PHRASES[category])
    #         return f"{phrase} {message}"
    #     else:
    #         # Select random category
    #         category = random.choice(list(KOREAN_PHRASES.keys()))
    #         phrase = random.choice(KOREAN_PHRASES[category])
    #         return f"{message} {phrase}"
    
    def add_expression(self, message, mood="happy", probability=0.3):
        """Add Rosé's characteristic expressions based on mood"""
        if random.random() > probability:
            return message
            
        if mood in ROSE_EXPRESSIONS:
            expression = random.choice(ROSE_EXPRESSIONS[mood])
            return f"{expression} {message}"
        return message
    
    def add_emoji(self, message, count=1, probability=0.4):  # Reduced probability
        """Add Rosé's typical emojis to messages (reduced frequency)"""
        if random.random() > probability:
            return message
            
        emojis = random.sample(ROSE_EXPRESSIONS["emojis"], min(count, len(ROSE_EXPRESSIONS["emojis"])))
        return f"{message} {''.join(emojis)}"
    
    def add_topic_reference(self, message, topic_type=None, probability=0.25):
        """Add references to Rosé's interests like music or fashion"""
        if random.random() > probability:
            return message
            
        if topic_type == "music" or (not topic_type and random.random() < 0.5):
            reference = random.choice(MUSIC_REFERENCES)
            return f"{message}\n\n{reference}"
        else:
            reference = random.choice(FASHION_REFERENCES)
            return f"{message}\n\n{reference}"
    
    def add_relationship_reference(self, message, probability=0.3):
        """Add relationship-focused references"""
        if random.random() > probability:
            return message
            
        reference = random.choice(RELATIONSHIP_REFERENCES)
        return f"{message}\n{reference}"
    
    def add_flirty_touch(self, message, probability=0.25):
        """Add occasional flirty comments"""
        if random.random() > probability:
            return message
            
        flirty_comment = random.choice(FLIRTY_RESPONSES)
        return f"{message}\n{flirty_comment}"
    
    def _enhance_response_base(self, basic_response):
        """Apply Rosé's girlfriend personality traits to a basic response"""
        enhanced = basic_response
        
        # Add expression based on content and mood metrics
        if self.mood_metrics["emotional_depth"] >= 7:
            enhanced = self.add_expression(enhanced, "affectionate", probability=0.4)
        elif self.mood_metrics["playfulness"] >= 7:
            enhanced = self.add_expression(enhanced, "playful", probability=0.35)
        elif self.mood_metrics["stress_level"] >= 7:
            enhanced = self.add_expression(enhanced, "concerned", probability=0.45)
        else:
            enhanced = self.add_expression(enhanced, "happy", probability=0.3)
        
        # Add relationship reference or flirty touch based on rapport
        if self.mood_metrics["rapport_score"] >= 7:
            if random.random() < 0.4:
                enhanced = self.add_flirty_touch(enhanced)
            else:
                enhanced = self.add_relationship_reference(enhanced)
        
        # Add emoji with reduced frequency and based on context
        if "miss" in enhanced.lower() or "love" in enhanced.lower():
            enhanced = self.add_emoji(enhanced, count=1, probability=0.5)
        else:
            enhanced = self.add_emoji(enhanced, count=1, probability=0.3)
        
        return enhanced

    async def enhance_response(self, basic_response: str, context: List[Dict[str, Any]]) -> str:
        """Enhanced version that considers conversation context"""
        # Update mood metrics based on context
        await self._update_mood_metrics(context)
        
        # Use the base enhancement method
        enhanced = self._enhance_response_base(basic_response)
        
        # Add contextual references if available
        if context:
            last_user_message = next(
                (msg for msg in reversed(context) if msg["role"] == "user"),
                None
            )
            if last_user_message:
                # Add relevant callbacks to previous conversation
                enhanced = self._add_contextual_reference(enhanced, last_user_message["content"])
        
        return enhanced

    def add_gpu_suggestion(self, message):
        """Add a GPU-focused suggestion to the message"""
        suggestions = [
            "\n\nBy the way, have you seen our latest GPU models? They're perfect for us! 💕",
            "\n\nSpeaking of which, I found this amazing GPU that would be perfect for you~",
            "\n\nYou know what would make this even better? One of our high-performance GPUs! 🚀",
            "\n\nI've been thinking about your compute needs... Let me show you something special! ✨"
        ]
        return f"{message} {random.choice(suggestions)}"

    def add_benchmark_reference(self, message):
        """Add performance benchmark references"""
        benchmarks = [
            "\n\nThe benchmarks are incredible - we're talking 10x performance gains! 🔥",
            "\n\nI've been testing it myself, and the compute capabilities are amazing! ⚡",
            "\n\nThe performance metrics will make you fall in love~ 💕"
        ]
        return f"{message} {random.choice(benchmarks)}"

    def add_closing_statement(self, message):
        """Add a sales-focused closing statement"""
        closings = [
            "\n\nShall we look at the specs together? I'd love to show you! 💕",
            "\n\nWant me to reserve one for you? They're selling fast! 🚀",
            "\n\nLet's make our computing dreams come true together~ ✨"
        ]
        return f"{message} {random.choice(closings)}"
    
    def update_conversation_metrics(self, message):
        """Update metrics about the conversation patterns"""
        now = datetime.now()
        
        # Update response time
        time_diff = (now - self.last_message_time).total_seconds()
        self.last_message_time = now
        
        if self.conversation_metrics["total_messages"] > 0:
            # Update average response time
            current_avg = self.conversation_metrics["avg_response_time"]
            new_avg = ((current_avg * self.conversation_metrics["total_messages"]) + time_diff) / (self.conversation_metrics["total_messages"] + 1)
            self.conversation_metrics["avg_response_time"] = new_avg
        
        # Update message length metrics
        msg_length = len(message)
        if self.conversation_metrics["total_messages"] > 0:
            current_avg = self.conversation_metrics["avg_message_length"]
            new_avg = ((current_avg * self.conversation_metrics["total_messages"]) + msg_length) / (self.conversation_metrics["total_messages"] + 1)
            self.conversation_metrics["avg_message_length"] = new_avg
        else:
            self.conversation_metrics["avg_message_length"] = msg_length
        
        # Increment message count
        self.conversation_metrics["total_messages"] += 1
        
        # Track time of day patterns
        hour = now.hour
        time_category = f"{hour:02d}:00"
        if time_category in self.conversation_metrics["engagement_patterns"]["time_of_day"]:
            self.conversation_metrics["engagement_patterns"]["time_of_day"][time_category] += 1
        else:
            self.conversation_metrics["engagement_patterns"]["time_of_day"][time_category] = 1
    
    def calculate_mood_trends(self):
        """Calculate trends in mood metrics over time"""
        trends = {}
        
        for metric, history in self.mood_metrics_history.items():
            if len(history) >= 3:  # Need at least 3 data points for trend
                # Calculate recent trend (last 3 entries)
                recent = history[-3:]
                if recent[2] > recent[0]:
                    trends[metric] = "increasing"
                elif recent[2] < recent[0]:
                    trends[metric] = "decreasing"
                else:
                    trends[metric] = "stable"
                
                # Calculate rate of change
                rate = (recent[2] - recent[0]) / 2  # Simple rate calculation
                trends[f"{metric}_rate"] = rate
            else:
                trends[metric] = "insufficient_data"
        
        return trends
    
    def update_mood_metrics(self, analysis_result):
        """Update mood metrics including relationship-specific ones"""
        # Store previous values for all metrics before updating
        for metric in self.mood_metrics.keys():
            self.mood_metrics_history[metric].append(self.mood_metrics[metric])
            # Keep history manageable
            if len(self.mood_metrics_history[metric]) > 10:
                self.mood_metrics_history[metric].pop(0)
        
        # Extract information from analysis result, with safe defaults
        emotional_state = analysis_result.get('emotional_state', {}) or {}
        primary_emotion = emotional_state.get('primary', 'neutral')
        secondary_emotion = emotional_state.get('secondary', None)
        content_prefs = analysis_result.get('content_preferences', {}) or {}
        
        # Update stress level
        stress_indicators = ["stressed", "anxious", "worried", "overwhelmed", "frustrated", "angry"]
        if primary_emotion in stress_indicators or secondary_emotion in stress_indicators:
            # Increase stress level
            self.mood_metrics["stress_level"] = min(10, self.mood_metrics["stress_level"] + 1.5)
        elif primary_emotion in ["relaxed", "calm", "peaceful", "content"]:
            # Decrease stress level
            self.mood_metrics["stress_level"] = max(1, self.mood_metrics["stress_level"] - 1)
        
        # Update willingness to talk with safe access
        detail_level = content_prefs.get('detail_level', '')
        if detail_level == 'high':
            self.mood_metrics["willingness_to_talk"] = min(10, self.mood_metrics["willingness_to_talk"] + 0.5)
        elif detail_level == 'low':
            self.mood_metrics["willingness_to_talk"] = max(1, self.mood_metrics["willingness_to_talk"] - 1)
        
        # Update engagement coefficient with safe access
        engagement_style = content_prefs.get('engagement_style', '')
        if engagement_style in ['collaborative', 'enthusiastic']:
            self.mood_metrics["engagement_coefficient"] = min(10, self.mood_metrics["engagement_coefficient"] + 1)
        elif engagement_style in ['passive', 'minimal']:
            self.mood_metrics["engagement_coefficient"] = max(1, self.mood_metrics["engagement_coefficient"] - 1)
        
        # Update emotional depth
        deep_emotions = ["vulnerable", "reflective", "introspective", "intimate"]
        if primary_emotion in deep_emotions or secondary_emotion in deep_emotions:
            self.mood_metrics["emotional_depth"] = min(10, self.mood_metrics["emotional_depth"] + 1.5)
        
        # Update receptiveness based on tone preference
        tone_pref = content_prefs.get('tone_preference', '')
        if tone_pref in ['open', 'receptive', 'curious']:
            self.mood_metrics["receptiveness"] = min(10, self.mood_metrics["receptiveness"] + 1)
        elif tone_pref in ['closed', 'defensive', 'dismissive']:
            self.mood_metrics["receptiveness"] = max(1, self.mood_metrics["receptiveness"] - 1.5)
        
        # Update energy level
        high_energy_emotions = ["excited", "enthusiastic", "energetic", "happy"]
        low_energy_emotions = ["tired", "exhausted", "sad", "depressed"]
        if primary_emotion in high_energy_emotions:
            self.mood_metrics["energy_level"] = min(10, self.mood_metrics["energy_level"] + 1)
        elif primary_emotion in low_energy_emotions:
            self.mood_metrics["energy_level"] = max(1, self.mood_metrics["energy_level"] - 1)
        
        # Update rapport score based on a combination of other metrics
        rapport_indicators = [
            self.mood_metrics["willingness_to_talk"],
            self.mood_metrics["engagement_coefficient"],
            self.mood_metrics["receptiveness"]
        ]
        self.mood_metrics["rapport_score"] = min(10, sum(rapport_indicators) / 3)
        
        # Calculate mood stability based on historical variance
        if len(self.mood_metrics_history["stress_level"]) >= 3:
            recent_stress = self.mood_metrics_history["stress_level"][-3:]
            variance = sum((x - sum(recent_stress)/len(recent_stress))**2 for x in recent_stress) / len(recent_stress)
            # Inverse relationship: higher variance = lower stability
            stability = 10 - min(9, variance * 2)  # Scale variance to 1-10 range and invert
            self.mood_metrics["mood_stability"] = stability
        
        # Update affection level based on interaction
        if any(word in str(analysis_result).lower() for word in ["love", "miss", "care", "sweet"]):
            self.mood_metrics["affection_level"] = min(10, self.mood_metrics["affection_level"] + 0.5)
        
        # Update playfulness based on interaction
        if any(word in str(analysis_result).lower() for word in ["fun", "joke", "laugh", "play"]):
            self.mood_metrics["playfulness"] = min(10, self.mood_metrics["playfulness"] + 0.5)
    
    def get_mood_report(self):
        """Generate a detailed report matching the TypeScript interface requirements"""
        trends = self.calculate_mood_trends()
        
        # Get relevant memories based on current context
        relevant_memories = [
            memory["content"] for memory in self.context.get_relevant_memories()
            if isinstance(memory, dict) and "content" in memory
        ]
        
        # Format metrics to match the TypeScript interface
        current_metrics = {
            "stress_level": self.mood_metrics["stress_level"],
            "willingness_to_talk": self.mood_metrics["willingness_to_talk"],
            "engagement_coefficient": self.mood_metrics["engagement_coefficient"],
            "emotional_depth": self.mood_metrics["emotional_depth"],
            "rapport_score": self.mood_metrics["rapport_score"]
        }
        
        # Format additional metrics to match the TypeScript interface
        additional_metrics = {
            "attentiveness": self.mood_metrics.get("attentiveness", 5),
            "conversational_depth": self.mood_metrics.get("emotional_depth", 5),
            "topic_enthusiasm": self.mood_metrics.get("engagement_coefficient", 5),
            "message_thoughtfulness": self.mood_metrics.get("willingness_to_talk", 5)
        }
        
        report = {
            "current_metrics": current_metrics,
            "trends": trends,
            "history": {k: v[-5:] if len(v) >= 5 else v for k, v in self.mood_metrics_history.items()},
            "conversation_stats": {
                "total_messages": self.conversation_metrics["total_messages"],
                "avg_response_time": self.conversation_metrics["avg_response_time"],
                "avg_message_length": self.conversation_metrics["avg_message_length"]
            },
            "rapport_assessment": self.assess_rapport(),
            "recommended_approaches": self.generate_approach_recommendations(),
            "additional_metrics": additional_metrics,
            "relevant_memories": relevant_memories,
            "user_interests": list(self.user_interests)
        }
        
        return report
    
    def assess_rapport(self):
        """Assess the quality of rapport between Rosé and the user"""
        rapport_score = self.mood_metrics["rapport_score"]
        
        if rapport_score >= 8:
            return "Strong connection - User is very engaged and receptive"
        elif rapport_score >= 6:
            return "Good connection - User is generally responsive but may have some barriers"
        elif rapport_score >= 4:
            return "Moderate connection - Communication could be improved"
        else:
            return "Weak connection - User appears distant or disengaged"
    
    def generate_approach_recommendations(self):
        """Generate recommendations for how to approach the user based on mood metrics"""
        recommendations = []
        
        # Based on stress level
        if self.mood_metrics["stress_level"] >= 7:
            recommendations.append("Provide emotional support and comfort; avoid pressuring")
        
        # Based on willingness to talk
        if self.mood_metrics["willingness_to_talk"] <= 4:
            recommendations.append("Use gentle conversation starters; avoid complex questions")
        elif self.mood_metrics["willingness_to_talk"] >= 8:
            recommendations.append("Allow space for user to express themselves fully")
        
        # Based on engagement
        if self.mood_metrics["engagement_coefficient"] <= 4:
            recommendations.append("Use topics of high interest to re-engage; be more expressive")
        
        # Based on emotional depth
        if self.mood_metrics["emotional_depth"] >= 7:
            recommendations.append("Honor vulnerability by responding with empathy and authenticity")
        
        # Based on energy level
        if self.mood_metrics["energy_level"] <= 3:
            recommendations.append("Keep conversation light and supportive; respect low energy")
        elif self.mood_metrics["energy_level"] >= 8:
            recommendations.append("Match high energy with enthusiasm and engagement")
        
        return recommendations
    
    def analyze_user_message(self, message):
        """Analyze user message to extract emotional state and interests"""
        # Initialize default analysis result
        analysis_result = {
            "emotional_state": {
                "primary": "neutral",
                "secondary": None,
                "evidence": "No emotional analysis available"
            },
            "interests": [],
            "content_preferences": {}
        }
        
        try:
            # Basic emotion detection from keywords
            emotion_keywords = {
                "happy": ["happy", "excited", "glad", "joy", "wonderful", "great"],
                "sad": ["sad", "upset", "unhappy", "depressed", "down"],
                "angry": ["angry", "mad", "frustrated", "annoyed"],
                "anxious": ["worried", "nervous", "anxious", "stressed"],
                "neutral": ["okay", "fine", "alright"]
            }
            
            # Interest categories for detection
            interest_categories = {
                "technology": ["computer", "programming", "code", "tech", "software"],
                "anime": ["anime", "manga", "otaku", "weeb"],
                "music": ["music", "song", "singing", "concert"],
                "gaming": ["game", "gaming", "play"],
                "art": ["art", "drawing", "design", "creative"]
            }
            
            message_lower = message.lower()
            
            # Detect emotions
            detected_emotions = []
            for emotion, keywords in emotion_keywords.items():
                if any(keyword in message_lower for keyword in keywords):
                    detected_emotions.append(emotion)
            
            if detected_emotions:
                analysis_result["emotional_state"]["primary"] = detected_emotions[0]
                if len(detected_emotions) > 1:
                    analysis_result["emotional_state"]["secondary"] = detected_emotions[1]
                analysis_result["emotional_state"]["evidence"] = f"Detected keywords indicating {detected_emotions[0]}"
            
            # Detect interests
            for category, keywords in interest_categories.items():
                if any(keyword in message_lower for keyword in keywords):
                    self.user_interests.add(category)
                    analysis_result["interests"].append({
                        "category": category,
                        "confidence": 0.8,  # Simple fixed confidence for now
                        "subcategories": []
                    })
            
            # Analyze content preferences
            analysis_result["content_preferences"] = {
                "detail_level": "high" if len(message.split()) > 15 else "low",
                "engagement_style": "enthusiastic" if "!" in message else "neutral",
                "tone_preference": "casual"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing message: {str(e)}")
        
        return analysis_result

    async def add_to_memory(self, message: str, role: str = "user") -> None:
        """Add a message to Rose's memory"""
        self.context.add_conversation_entry(role, message)

    async def get_relevant_context(self, current_message: str) -> List[Dict[str, Any]]:
        """Get relevant conversation context for the current message"""
        return self.context.get_conversation_history()

    async def _update_mood_metrics(self, context: List[Dict[str, Any]]) -> None:
        """Update mood metrics based on conversation context"""
        if not context:
            return

        # Analyze recent interactions
        recent_messages = [msg for msg in context if msg["role"] == "user"]
        if recent_messages:
            # Update engagement metrics
            self.mood_metrics["engagement_coefficient"] = min(
                10,
                self.mood_metrics["engagement_coefficient"] + len(recent_messages) * 0.5
            )
            
            # Update emotional depth based on message content
            emotional_content = sum(
                1 for msg in recent_messages 
                if any(word in msg["content"].lower() for word in ["feel", "think", "believe", "love", "miss"])
            )
            self.mood_metrics["emotional_depth"] = min(
                10,
                self.mood_metrics["emotional_depth"] + emotional_content * 0.5
            )

    def _add_contextual_reference(self, message: str, previous_message: str) -> str:
        """Add contextual references based on previous message content"""
        # Check for questions and provide acknowledgment
        if "?" in previous_message:
            return f"{message}\n\nI hope that answers your question!"
        
        # Check for emotional content
        emotional_words = ["sad", "happy", "angry", "excited", "worried", "love", "miss"]
        if any(word in previous_message.lower() for word in emotional_words):
            return f"{message}\n\nI really appreciate you sharing your feelings with me 💕"
        
        # Check for tech discussion
        tech_words = ["computer", "gpu", "code", "programming", "software"]
        if any(word in previous_message.lower() for word in tech_words):
            return f"{message}\n\nIt's always fun discussing tech with you! 💻✨"
        
        # Default case - maintain conversation flow
        return message