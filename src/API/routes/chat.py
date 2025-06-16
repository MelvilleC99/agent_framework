# src/api/routes/chat.py
"""
Chat API Routes

Handles agent chat interactions, session management, and cost tracking.
Based on the Industrial Engineering Agent chat.py implementation.
"""

import time
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, Body, HTTPException
from pydantic import BaseModel

logger = logging.getLogger("chat_api")

router = APIRouter()

# Active sessions storage
active_sessions = {}


class ChatRequest(BaseModel):
    """Chat request model"""
    query: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    answer: str
    session_id: str
    user_id: Optional[str] = None
    token_usage: Optional[Dict[str, Any]] = None
    execution_time_seconds: float
    sessionEnded: Optional[bool] = None


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: Request, payload: ChatRequest):
    """
    Process a chat request through the agent system.
    
    Args:
        request: FastAPI request object (contains injected dependencies)
        payload: Chat request payload
        
    Returns:
        ChatResponse with agent answer and metadata
    """
    start_time = time.time()
    query = payload.query
    session_id = payload.session_id
    user_id = payload.user_id
    
    logger.info(f"Received query: {query} from user: {user_id or 'anonymous'}")
    
    try:
        # Access injected dependencies
        orchestrator = request.app.state.orchestrator
        container = request.app.state.container
        settings = request.app.state.settings
        
        # Handle session management
        if not session_id:
            session_id = f"sess_{int(time.time())}"
            logger.info(f"Created new session: {session_id} for user: {user_id or 'anonymous'}")
        
        # Get or create session manager
        if session_id not in active_sessions:
            from ...orchestration.session_manager import SessionManager
            active_sessions[session_id] = SessionManager(
                session_id, 
                timeout_minutes=settings.max_session_duration_minutes
            )
            logger.info(f"Initialized session manager for {session_id}")
        
        session_manager = active_sessions[session_id]
        
        # Check if session has expired
        if session_manager.is_session_expired():
            logger.info(f"Session {session_id} has expired, ending and creating summary")
            orchestrator.end_session(session_id, reason="timeout", user_id=user_id)
            del active_sessions[session_id]
            
            # Create new session
            session_id = f"sess_{int(time.time())}"
            active_sessions[session_id] = SessionManager(
                session_id, 
                timeout_minutes=settings.max_session_duration_minutes
            )
            session_manager = active_sessions[session_id]
            logger.info(f"Created new session after timeout: {session_id}")
        
        # Update session activity
        session_manager.update_activity()
        
        # Set session ID in orchestrator
        orchestrator.set_session_id(session_id)
        
        # Process through orchestrator
        response = orchestrator.process_query(query, user_id=user_id)
        
        execution_time = time.time() - start_time
        logger.info(f"Query processed in {execution_time:.2f} seconds")
        
        # Add session ID and token usage statistics to response
        token_usage = orchestrator.get_token_usage()
        response["session_id"] = session_id
        response["user_id"] = user_id
        response["token_usage"] = token_usage
        response["execution_time_seconds"] = round(execution_time, 2)
        
        # Check if session should end due to goodbye
        should_end_session = response.get("session_will_end", False) or response.get("end_session", False)
        if should_end_session:
            response["sessionEnded"] = True
            logger.info(f"Session {session_id} will end after response")
            
            # End session in background
            import threading
            def delayed_session_end():
                import time
                time.sleep(0.5)  # Wait for usage log to be written
                try:
                    success = orchestrator.end_session(session_id, reason="user_goodbye", user_id=user_id)
                    if success:
                        logger.info(f"Session {session_id} ended and summarized successfully")
                    if session_id in active_sessions:
                        del active_sessions[session_id]
                except Exception as e:
                    logger.error(f"Error in delayed session end: {e}")
            
            threading.Thread(target=delayed_session_end, daemon=True).start()
        
        return ChatResponse(**response)
        
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        return ChatResponse(
            answer=f"I'm sorry, I encountered an error while processing your query: {str(e)}",
            session_id=session_id or f"sess_{int(time.time())}",
            user_id=user_id,
            execution_time_seconds=round(time.time() - start_time, 2)
        )

@router.get("/token-usage")
async def get_token_usage(request: Request):
    """Get token usage statistics for the current session."""
    try:
        orchestrator = request.app.state.orchestrator
        token_usage = orchestrator.get_token_usage()
        return token_usage
    except Exception as e:
        logger.error(f"Error getting token usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/end_session")
async def end_session(request: Request, payload: Dict[str, Any] = Body(...)):
    """End a session manually and create summary."""
    session_id = payload.get("session_id")
    user_id = payload.get("user_id")
    
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")
    
    try:
        orchestrator = request.app.state.orchestrator
        
        # End session in orchestrator (creates summary)
        success = orchestrator.end_session(session_id, reason="manual", user_id=user_id)
        
        # Remove from active sessions
        if session_id in active_sessions:
            del active_sessions[session_id]
        
        return {
            "status": "success" if success else "warning",
            "message": f"Session {session_id} ended {'successfully' if success else 'with issues'}",
            "session_id": session_id,
            "user_id": user_id
        }
    except Exception as e:
        logger.error(f"Error ending session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/session_info/{session_id}")
async def get_session_info(session_id: str):
    """Get information about a specific session."""
    try:
        if session_id in active_sessions:
            session_manager = active_sessions[session_id]
            return session_manager.get_session_info()
        else:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found or expired")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active_sessions")
async def get_active_sessions():
    """Get list of all active sessions."""
    try:
        session_info = {}
        for session_id, session_manager in active_sessions.items():
            session_info[session_id] = session_manager.get_session_duration()
        
        return {
            "active_session_count": len(active_sessions),
            "sessions": session_info
        }
    except Exception as e:
        logger.error(f"Error getting active sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))
