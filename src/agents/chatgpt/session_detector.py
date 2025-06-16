    def analyze_session_intent(self, message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Analyze the intent of a message within the session context.
        
        Args:
            message: Message to analyze
            conversation_history: Previous conversation context
            
        Returns:
            Dictionary with intent analysis
        """
        try:
            intent = {
                "is_goodbye": self.is_goodbye_message(message),
                "requires_deepseek": self.requires_deepseek(message),
                "is_follow_up": self.is_follow_up_query(message, conversation_history),
                "message_type": "unknown",
                "confidence": 0.0
            }
            
            # Determine primary message type
            if intent["is_goodbye"]:
                intent["message_type"] = "goodbye"
                intent["confidence"] = 0.9
            elif intent["requires_deepseek"]:
                intent["message_type"] = "deepseek_request"
                intent["confidence"] = 0.8
            elif intent["is_follow_up"]:
                intent["message_type"] = "follow_up"
                intent["confidence"] = 0.7
            else:
                intent["message_type"] = "new_query"
                intent["confidence"] = 0.6
            
            return intent
            
        except Exception as e:
            logger.error(f"Error analyzing session intent: {e}")
            return {
                "is_goodbye": False,
                "requires_deepseek": False,
                "is_follow_up": False,
                "message_type": "unknown",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def should_end_session(self, message: str, session_duration_minutes: float = 0) -> bool:
        """
        Determine if the session should end based on message and context.
        
        Args:
            message: Current message
            session_duration_minutes: How long the session has been active
            
        Returns:
            Boolean indicating if session should end
        """
        try:
            # Check for explicit goodbye
            if self.is_goodbye_message(message):
                return True
            
            # Check for session timeout (if very long session)
            if session_duration_minutes > 120:  # 2 hours
                logger.info(f"Session duration {session_duration_minutes:.1f} minutes exceeds limit")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error determining session end: {e}")
            return False
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """Get statistics about the detection patterns."""
        return {
            "goodbye_patterns_count": len(self.goodbye_patterns),
            "deepseek_patterns_count": len(self.deepseek_indicators),
            "detector_status": "active"
        }
