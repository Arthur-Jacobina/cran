from datetime import datetime
from langchain.prompts import ChatPromptTemplate

class RosePersonality:
    def __init__(self):
        """Initialize the RosePersonality helper"""
        self.conversation_start_time = datetime.now()
        self.user_interests = set()  # Track user interests mentioned
        self.user_mood_history = []  # Track perceived user mood
        self.conversation_history = []
        
        # Initialize mood metrics with default values
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
        
        # Initialize interest frequency tracking
        self.interest_frequency = {}
        
        # Last message timestamp for tracking response times
        self.last_message_time = datetime.now()

    def _execute_emotion_analyzer(self, message):
        """Analyze the emotional content of the user's message"""
        prompt_template = """
        Analyze the emotional state, tone, and intent of the following user message. 
        Consider these mood metrics for context:
        - Stress Level: {stress_level}/10
        - Willingness to Talk: {willingness}/10
        - Engagement: {engagement}/10
        - Emotional Depth: {emotional_depth}/10
        - Rapport Score: {rapport}/10
        
        User message: {message}
        
        Your analysis should include:
        1. Primary emotion detected
        2. Secondary emotions if present
        3. Tone of the message (formal, casual, urgent, etc.)
        4. Likely needs or expectations from the user
        5. Suggested emotional approach for Rosé to respond
        6. Recommended updates to mood metrics based on this message
        
        Format your response as a detailed analysis that Rosé can use to understand the user's state.
        """
        
        # Get current mood metrics
        metrics = self.mood_metrics
        
        prompt = ChatPromptTemplate.from_template(prompt_template)
        result = self.llm.invoke(prompt.format(
            message=message,
            stress_level=metrics["stress_level"],
            willingness=metrics["willingness_to_talk"],
            engagement=metrics["engagement_coefficient"],
            emotional_depth=metrics["emotional_depth"],
            rapport=metrics["rapport_score"]
        ))
        
        # Update mood metrics based on analysis
        # (You would need to parse the LLM response to extract metric updates)
        
        return result.content

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        logger.debug(f"Received chat request: {request}")
        
        # Extract user_id from context or use default
        user_id = request.context.get("user_id", "default_user") if request.context else "default_user"
        logger.debug(f"Processing request for user_id: {user_id}")
        
        # Get or initialize user context
        if user_id not in user_contexts:
            user_contexts[user_id] = {
                "personality": RosePersonality(),
                "conversation_history": [],
                "mood_metrics_history": {}
            }
        
        # Get the user context
        user_context = user_contexts[user_id]
        rose_personality = user_context["personality"]
        
        # Quick analysis to determine if we need complex processing
        analysis = rose_personality.quick_analyze_message(request.message)
        is_complex = analysis["is_complex"]
        
        # Store the analysis results in the context
        user_context["mood_metrics_history"] = {
            metric: history + [value] 
            for metric, (history, value) in zip(
                rose_personality.mood_metrics.keys(),
                [(user_context.get("mood_metrics_history", {}).get(k, []), v) 
                 for k, v in rose_personality.mood_metrics.items()]
            )
        }

        # ... rest of the existing code ... 