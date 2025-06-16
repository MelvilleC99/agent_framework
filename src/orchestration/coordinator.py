                from ..agents.deepseek.core_agent import DeepSeekAgent
                self.deepseek_agent = DeepSeekAgent(
                    database=self.database
                )
                logger.info("DeepSeek agent initialized")
            except ImportError as e:
                logger.error(f"Failed to import DeepSeek agent: {e}")
                # DeepSeek is optional, continue without it
                self.deepseek_agent = None
    
    def process_query(self, query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a user query through the two-tier system.
        
        Args:
            query: The user's query
            user_id: Optional user identifier for tracking
            
        Returns:
            Response dictionary with answer and metadata
        """
        start_time = time.time()
        logger.info(f"Processing query: {query} for user: {user_id or 'anonymous'}")
        
        # Generate tracking IDs
        session_id = getattr(self, '_current_session_id', f"sess_{int(time.time())}")
        conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
        
        # Start cost tracking
        if self.usage_tracker:
            try:
                self.usage_tracker.start_query_tracking(
                    session_id=session_id,
                    conversation_id=conversation_id,
                    query_text=query,
                    user_id=user_id
                )
            except Exception as e:
                logger.warning(f"Failed to start usage tracking: {e}")
        
        # Add query to context manager
        self.context_manager.add_message("user", query)
        
        try:
            # Initialize ChatGPT agent if needed
            self._initialize_chatgpt_agent()
            
            # Process with ChatGPT first
            recent_history = self.context_manager.get_recent_history(6)
            gpt_result = self.chatgpt_agent.process_query(
                query, 
                conversation_history=recent_history,
                conversation_id=conversation_id
            )
            
            # Check if DeepSeek is needed
            if gpt_result.get("requires_deepseek", False):
                logger.info("Query requires DeepSeek, attempting handoff")
                handoff_context = self.context_manager.get_summary_for_handoff()
                deepseek_result = self._call_deepseek(query, handoff_context, conversation_id)
                
                if deepseek_result.get("answer"):
                    self.context_manager.add_message("assistant", deepseek_result["answer"])
                    
                    # Complete tracking for DeepSeek handoff
                    if self.usage_tracker:
                        try:
                            self.usage_tracker.complete_query_tracking(
                                conversation_id=conversation_id,
                                success=True,
                                handed_to_deepseek=True
                            )
                        except Exception as e:
                            logger.warning(f"Failed to complete usage tracking: {e}")
                    
                    execution_time = time.time() - start_time
                    logger.info(f"Query processed with DeepSeek in {execution_time:.2f} seconds")
                    return deepseek_result
            
            # ChatGPT handled it successfully
            if gpt_result.get("answer"):
                self.context_manager.add_message("assistant", gpt_result["answer"])
                
                # Check if user said goodbye (end session)
                if gpt_result.get("is_goodbye", False):
                    logger.info(f"User said goodbye, marking session {session_id} for end")
                    gpt_result["session_will_end"] = True
                
                # Complete tracking for successful ChatGPT query
                if self.usage_tracker:
                    try:
                        self.usage_tracker.complete_query_tracking(
                            conversation_id=conversation_id,
                            success=True,
                            response_type=gpt_result.get("response_type", "text")
                        )
                    except Exception as e:
                        logger.warning(f"Failed to complete usage tracking: {e}")
                
                execution_time = time.time() - start_time
                logger.info(f"Query processed with ChatGPT in {execution_time:.2f} seconds")
                return gpt_result
            
            # If there was an error with ChatGPT, try DeepSeek as fallback
            if gpt_result.get("error"):
                logger.error(f"Error with ChatGPT: {gpt_result['error']}")
                
                # Try DeepSeek as fallback
                deepseek_result = self._call_deepseek(query, None, conversation_id)
                
                if deepseek_result.get("answer"):
                    self.context_manager.add_message("assistant", deepseek_result["answer"])
                    execution_time = time.time() - start_time
                    logger.info(f"Query processed with DeepSeek (fallback) in {execution_time:.2f} seconds")
                    return deepseek_result
                
                # Complete tracking for failed query
                if self.usage_tracker:
                    try:
                        self.usage_tracker.complete_query_tracking(
                            conversation_id=conversation_id,
                            success=False,
                            error_message=gpt_result["error"]
                        )
                    except Exception as e:
                        logger.warning(f"Failed to complete usage tracking: {e}")
            
            # If we get here, something unexpected happened
            if self.usage_tracker:
                try:
                    self.usage_tracker.complete_query_tracking(
                        conversation_id=conversation_id,
                        success=False,
                        error_message="Unexpected response format from ChatGPT"
                    )
                except Exception as e:
                    logger.warning(f"Failed to complete usage tracking: {e}")
            
            return {
                "answer": "I apologize, but I encountered an unexpected error while processing your query.",
                "error": "Unexpected response format from ChatGPT"
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            
            # Complete tracking for exception
            if self.usage_tracker:
                try:
                    self.usage_tracker.complete_query_tracking(
                        conversation_id=conversation_id,
                        success=False,
                        error_message=str(e)
                    )
                except Exception as tracking_error:
                    logger.warning(f"Failed to complete usage tracking after exception: {tracking_error}")
            
            return {
                "answer": f"I apologize, but I encountered an error while processing your query: {str(e)}",
                "error": str(e)
            }
    
    def _call_deepseek(self, query: str, context: Optional[str] = None, conversation_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Call the DeepSeek agent.
        
        Args:
            query: The user's query
            context: Optional context for the query
            conversation_id: Optional conversation ID for tracking
            
        Returns:
            Response from DeepSeek
        """
        # Initialize DeepSeek agent if not already done
        self._initialize_deepseek_agent()
        
        if self.deepseek_agent is None:
            logger.error("DeepSeek agent not available")
            return {
                "answer": "I'm sorry, I'm unable to analyze this deeply right now. The advanced analytics module is not available.",
                "error": "DeepSeek agent not available"
            }
        
        try:
            # Prepare the query with context if available
            if context:
                enhanced_query = f"CONTEXT: {context}\n\nQUERY: {query}"
            else:
                enhanced_query = query
            
            # Run the DeepSeek agent
            result = self.deepseek_agent.run(enhanced_query)
            
            return {
                "answer": result,
                "used_deepseek": True
            }
        except Exception as e:
            logger.error(f"Error calling DeepSeek agent: {e}")
            return {
                "answer": f"I apologize, but I encountered an error while attempting to analyze this deeply: {str(e)}",
                "error": str(e)
            }
    
    def get_token_usage(self) -> Dict[str, Any]:
        """
        Get token usage statistics for the current session.
        
        Returns:
            Dictionary containing token usage statistics
        """
        try:
            if self.chatgpt_agent and hasattr(self.chatgpt_agent, 'token_tracker'):
                return self.chatgpt_agent.token_tracker.get_session_summary()
            else:
                # Fallback to global token tracker
                from ..usage_tracking.token_tracker import token_tracker
                return token_tracker.get_session_summary()
        except Exception as e:
            logger.error(f"Error getting token usage: {e}")
            return {"error": str(e)}
    
    def set_session_id(self, session_id: str):
        """Set the current session ID for tracking."""
        self._current_session_id = session_id
        logger.info(f"Session ID set to: {session_id}")
    
    def end_session(self, session_id: Optional[str] = None, reason: str = "manual", user_id: Optional[str] = None) -> bool:
        """
        End the current session and create summary.
        
        Args:
            session_id: Session ID to end (uses current if not provided)
            reason: Reason for session end ('manual', 'timeout', 'logout')
            user_id: User ID for the session summary
            
        Returns:
            True if session ended successfully
        """
        if not session_id:
            session_id = getattr(self, '_current_session_id', None)
            if not session_id:
                logger.warning("No session ID provided for session end")
                return False
        
        try:
            # Create session summary
            if self.session_summarizer:
                success = self.session_summarizer.create_session_summary(
                    session_id=session_id,
                    user_id=user_id,
                    session_ended_reason=reason
                )
                
                if success:
                    logger.info(f"Session {session_id} ended and summarized for user: {user_id or 'anonymous'}")
                    # Clear current session if it matches
                    if hasattr(self, '_current_session_id') and self._current_session_id == session_id:
                        self._current_session_id = None
                else:
                    logger.warning(f"Session {session_id} ended but summary creation failed")
                
                return success
            else:
                logger.warning("Session summarizer not available")
                return False
            
        except Exception as e:
            logger.error(f"Error ending session {session_id}: {e}")
            return False
    
    def refresh_date(self):
        """Refresh the cached date in agents - useful for long-running sessions."""
        try:
            if self.chatgpt_agent:
                self.chatgpt_agent.refresh_date()
                logger.info("Date refreshed in ChatGPT agent")
        except Exception as e:
            logger.error(f"Error refreshing date: {e}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about the current session."""
        try:
            context_stats = self.context_manager.get_conversation_stats()
            token_usage = self.get_token_usage()
            
            return {
                "session_id": self._current_session_id,
                "conversation_stats": context_stats,
                "token_usage": token_usage,
                "agents_initialized": {
                    "chatgpt": self.chatgpt_agent is not None,
                    "deepseek": self.deepseek_agent is not None
                }
            }
        except Exception as e:
            logger.error(f"Error getting session stats: {e}")
            return {"error": str(e)}
    
    def clear_context(self):
        """Clear the conversation context."""
        try:
            self.context_manager.clear_history()
            logger.info("Conversation context cleared")
        except Exception as e:
            logger.error(f"Error clearing context: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of all coordinator components."""
        try:
            health = {
                "coordinator": "healthy",
                "context_manager": "healthy" if self.context_manager else "unhealthy",
                "database": "healthy" if self.database else "unhealthy",
                "redis": "healthy" if self.redis else "not_configured",
                "tool_registry": "healthy" if self.tool_registry else "unhealthy",
                "usage_tracker": "healthy" if self.usage_tracker else "not_configured",
                "session_summarizer": "healthy" if self.session_summarizer else "not_configured",
                "agents": {
                    "chatgpt": "initialized" if self.chatgpt_agent else "not_initialized",
                    "deepseek": "initialized" if self.deepseek_agent else "not_initialized"
                }
            }
            
            return health
        except Exception as e:
            logger.error(f"Error in health check: {e}")
            return {"coordinator": "unhealthy", "error": str(e)}
