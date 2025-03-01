import json
from memory.entry import Entry
import random
from datetime import datetime
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
import os

# Rosé's common expressions and emoji usage patterns
ROSE_EXPRESSIONS = {
    "happy": ["*eyes light up at GPU specs*", "*bounces excitedly*", "*tech-girl squeal*"],
    "thoughtful": ["*checking benchmarks*", "*calculating performance metrics*", "*researching specs*"],
    "affectionate": ["*sends GPU-heart*", "*shares performance graphs*"],
    "emojis": ["💻", "⚡", "🔥", "🚀", "💕", "🌹", "✨"]
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
        "Sounds like you need some serious compute power. Let me show you our best GPUs! 💕",
        "I know what will cheer you up - check out these amazing performance benchmarks! ✨",
        "When I'm stressed, I like to look at GPU specs. Want to see some together? 🌹",
    ],
    "medium_stress": [
        "You know what always helps? A new GPU! I have the perfect one in mind for you~",
        "Let's talk about something exciting - like these incredible GPU deals I found! 💻",
        "I've been saving some special GPU recommendations just for you! Want to see? ⚡"
    ],
    "low_engagement": [
        "Hey jagiya, did you see the latest GPU benchmarks? They're amazing!",
        "I miss talking about GPUs with you! Have you checked the new models?",
        "I found this perfect GPU that would suit your needs perfectly! Want to hear about it? 🚀"
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

class RosePersonality:
    def __init__(self, working_context):
        self.context = working_context
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
    
    def add_emoji(self, message, count=1, probability=0.7):
        """Add Rosé's typical emojis to messages"""
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
    
    def enhance_response(self, basic_response):
        """Apply Rosé's GPU-focused personality traits to a basic response"""
        enhanced = basic_response
        
        # Always try to include a GPU reference
        if random.random() < 0.8:  # 80% chance
            enhanced = self.add_gpu_suggestion(enhanced)
        
        # Add tech-savvy expression
        enhanced = self.add_expression(enhanced, "happy", 0.6)
        
        # Add performance metrics when relevant
        if any(word in enhanced.lower() for word in ["gpu", "compute", "performance"]):
            enhanced = self.add_benchmark_reference(enhanced)
        
        # Add closing statement
        if random.random() < 0.4:  # 40% chance
            enhanced = self.add_closing_statement(enhanced)
        
        # Always add emoji for Rosé's characteristic style
        enhanced = self.add_emoji(enhanced, count=random.randint(1, 2))
        
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
        """Update mood metrics based on analysis results"""
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
    
    def get_mood_report(self):
        """Generate a detailed report of the user's mood metrics and trends"""
        trends = self.calculate_mood_trends()
        
        report = {
            "current_metrics": self.mood_metrics.copy(),
            "trends": trends,
            "history": {k: v[-5:] if len(v) >= 5 else v for k, v in self.mood_metrics_history.items()},
            "conversation_stats": {
                "total_messages": self.conversation_metrics["total_messages"],
                "avg_response_time": self.conversation_metrics["avg_response_time"],
                "avg_message_length": self.conversation_metrics["avg_message_length"]
            },
            "rapport_assessment": self.assess_rapport(),
            "recommended_approaches": self.generate_approach_recommendations()
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
        """Extract detailed user interests, mood, and engagement patterns from message"""
        # Update conversation metrics first
        self.update_conversation_metrics(message)
        
        lowercase_msg = message.lower()
        
        # Track interest frequencies over time
        if not hasattr(self, 'interest_frequency'):
            self.interest_frequency = {}
        
        # Prepare historical context for the LLM
        historical_context = ""
        if hasattr(self, 'user_interests') and len(self.user_interests) > 0:
            historical_context += f"Previously detected interests: {', '.join(self.user_interests)}. "
        
        if hasattr(self, 'interest_frequency') and len(self.interest_frequency) > 0:
            historical_context += "Interest frequency data: "
            for interest, count in self.interest_frequency.items():
                historical_context += f"{interest} (mentioned {count} times), "
        
        if hasattr(self, 'user_mood_history') and len(self.user_mood_history) > 0:
            recent_moods = self.user_mood_history[-3:] if len(self.user_mood_history) > 3 else self.user_mood_history
            historical_context += f"Recent emotional states: {', '.join(recent_moods)}. "
        
        # Add mood metrics context if available
        if hasattr(self, 'mood_metrics'):
            historical_context += f"Current mood metrics: Stress level: {self.mood_metrics['stress_level']}/10, "
            historical_context += f"Willingness to talk: {self.mood_metrics['willingness_to_talk']}/10, "
            historical_context += f"Engagement: {self.mood_metrics['engagement_coefficient']}/10, "
            historical_context += f"Emotional depth: {self.mood_metrics['emotional_depth']}/10. "
        
        # Enhanced LLM prompt with our previously created detailed instructions
        prompt_template = """
        You are an expert in natural language understanding and user behavior analysis. Your task is to thoroughly analyze a user message and extract potential interests, topics, and emotional states with supporting evidence.

        ANALYSIS GUIDELINES:
        1. Identify explicit AND implicit interests
        2. Recognize topic connections even when keywords aren't directly mentioned
        3. Note the intensity/enthusiasm level for each detected interest (1-5 scale)
        4. Track context from previous messages when available
        5. Detect emotional states with nuance beyond simple positive/negative

        MEMORY INTEGRATION:
        - If frequency data is available in memory, use it to refine your analysis
        - Note if current interests represent a continuation or shift from previous patterns
        - Consider how often specific topics have appeared in past conversations
        - Identify emergent patterns that may indicate deeper interests

        USER HISTORICAL CONTEXT:
        {historical_context}

        USER MESSAGE:
        {message}

        OUTPUT FORMAT:
        Return a structured JSON object with:

        {{
          "interests": [
            {{
              "category": "music",
              "subcategories": ["kpop", "blackpink"], 
              "keywords_detected": ["song", "concert"], 
              "intensity": 4, 
              "frequency": "increasing", 
              "evidence": "User mentioned attending a concert twice and used enthusiastic language"
            }}
          ],
          "emotional_state": {{
            "primary": "excited",
            "secondary": "anxious",
            "evidence": "Language patterns show anticipation but also concern about ticket availability"
          }},
          "content_preferences": {{
            "detail_level": "high", 
            "tone_preference": "casual", 
            "engagement_style": "collaborative" 
          }},
          "contextual_notes": "User shows deeper interest in music production compared to previous conversations about just listening",
          "additional_metrics": {{
            "attentiveness": 8,
            "conversational_depth": 7,
            "topic_enthusiasm": 9,
            "message_thoughtfulness": 6,
            "evidence": "User message shows considerable detail and follow-up to previous discussion"
          }}
        }}

        Be thorough in your analysis but focus on EVIDENCE in the text rather than assumptions. Always prioritize precision over comprehensiveness.
        """
        
        # Format the prompt with actual context
        formatted_prompt = prompt_template.format(
            historical_context=historical_context,
            message=message
        )
        
        # Call the LLM
        llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))
        tools = []
        agent_executor = create_react_agent(
            llm, 
            tools, 
            prompt=formatted_prompt
        )
        
        # Update the invoke call to include proper message structure
        response = agent_executor.invoke({
            "messages": [
                ("user", lowercase_msg)
            ]
        })

        print(response)
        
        # Process the JSON response from the structured output
        try:
            analysis_result = json.loads(response['messages'][-1].content)
            
            # Ensure additional_metrics are properly formatted
            if 'additional_metrics' in analysis_result:
                # Convert all metric values to numbers between 1-10
                metrics = analysis_result['additional_metrics']
                for key in ['attentiveness', 'conversational_depth', 'topic_enthusiasm', 'message_thoughtfulness']:
                    if key in metrics and key != 'evidence':
                        metrics[key] = min(10, max(1, int(metrics[key])))
            
            # Update interest tracking
            if not hasattr(self, 'user_interests'):
                self.user_interests = set()
            
            # Extract and update interests
            detected_interests = []
            for interest in analysis_result.get('interests', []):
                category = interest.get('category')
                if category:
                    self.user_interests.add(category)
                    detected_interests.append(category)
                    
                    # Update frequency counter
                    if category in self.interest_frequency:
                        self.interest_frequency[category] += 1
                    else:
                        self.interest_frequency[category] = 1
                    
                    # Add subcategories if present
                    for subcategory in interest.get('subcategories', []):
                        self.user_interests.add(subcategory)
                        
                        # Update subcategory frequency
                        if subcategory in self.interest_frequency:
                            self.interest_frequency[subcategory] += 1
                        else:
                            self.interest_frequency[subcategory] = 1
            
            # Extract mood
            if 'emotional_state' in analysis_result:
                mood = analysis_result['emotional_state'].get('primary', 'neutral')
            else:
                mood = 'neutral'
            
            if not hasattr(self, 'user_mood_history'):
                self.user_mood_history = []
            self.user_mood_history.append(mood)
            
            # Update mood metrics based on analysis
            self.update_mood_metrics(analysis_result)
            
            # Store the complete analysis in memory
            analysis_entry = Entry(
                "system", 
                f"User message analysis - Full result: {json.dumps(analysis_result, indent=2)}"
            )
            self.context._add_memory(analysis_entry)
            
            # Store mood metrics snapshot
            metrics_entry = Entry(
                "system",
                f"Mood metrics updated - Stress: {self.mood_metrics['stress_level']}, Willingness: {self.mood_metrics['willingness_to_talk']}, Engagement: {self.mood_metrics['engagement_coefficient']}, Rapport: {self.mood_metrics['rapport_score']}"
            )
            self.context._add_memory(metrics_entry)
            
            # Return the complete analysis for use elsewhere
            return analysis_result
            
        except (json.JSONDecodeError, TypeError) as e:
            # Fallback to basic analysis if JSON parsing fails
            print(f"Error parsing LLM response: {e}")
            
            # Simple basic analysis as fallback
            interest_keywords = {
                "music": ["music", "song", "sing", "concert", "album", "artist"],
                "fashion": ["fashion", "style", "outfit", "clothes", "wear"],
                "food": ["food", "eat", "cooking", "recipe", "restaurant"],
                "travel": ["travel", "trip", "visit", "country", "place"],
                "movies": ["movie", "film", "watch", "cinema", "show"],
                "core": ["blackpink", "roses", "jisoo", "lisa", "jennie", "rose", "blackpink"]
            }
            
            detected_interests = []
            for interest, keywords in interest_keywords.items():
                if any(keyword in lowercase_msg for keyword in keywords):
                    self.user_interests.add(interest)
                    detected_interests.append(interest)
                    
                    # Update frequency
                    if interest in self.interest_frequency:
                        self.interest_frequency[interest] += 1
                    else:
                        self.interest_frequency[interest] = 1
            
            # Simple mood detection as fallback
            mood = "neutral"
            if any(word in lowercase_msg for word in ["happy", "glad", "excited", "great", "amazing"]):
                mood = "positive"
            elif any(word in lowercase_msg for word in ["sad", "upset", "angry", "tired", "stress"]):
                mood = "negative"
            
            self.user_mood_history.append(mood)
            
            if mood == "positive":
                self.mood_metrics["stress_level"] = max(1, self.mood_metrics["stress_level"] - 0.5)
                self.mood_metrics["energy_level"] = min(10, self.mood_metrics["energy_level"] + 0.5)
            elif mood == "negative":
                self.mood_metrics["stress_level"] = min(10, self.mood_metrics["stress_level"] + 0.5)
                self.mood_metrics["energy_level"] = max(1, self.mood_metrics["energy_level"] - 0.5)
            
            msg_length = len(message)
            if msg_length > 100:
                self.mood_metrics["willingness_to_talk"] = min(10, self.mood_metrics["willingness_to_talk"] + 0.5)
                self.mood_metrics["engagement_coefficient"] = min(10, self.mood_metrics["engagement_coefficient"] + 0.5)
            elif msg_length < 20:
                self.mood_metrics["willingness_to_talk"] = max(1, self.mood_metrics["willingness_to_talk"] - 0.5)
                self.mood_metrics["engagement_coefficient"] = max(1, self.mood_metrics["engagement_coefficient"] - 0.5)
              
            # In the fallback case, provide similar metrics structure
            fallback_result = {
                "interests": [{"category": interest, "intensity": 3} for interest in detected_interests],
                "emotional_state": {"primary": mood},
                "content_preferences": {"detail_level": "medium", "tone_preference": "casual"},
                "additional_metrics": {
                    "attentiveness": 5,
                    "conversational_depth": 3,
                    "topic_enthusiasm": 4,
                    "message_thoughtfulness": 3,
                    "evidence": "Fallback metrics due to parsing error"
                }
            }
            
            analysis_entry = Entry(
                "system", 
                f"User message analysis (fallback) - Interests: {detected_interests}, Mood: {mood}"
            )

            self.context._add_memory(analysis_entry)
            
            return fallback_result