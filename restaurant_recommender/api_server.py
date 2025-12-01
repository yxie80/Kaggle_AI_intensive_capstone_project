"""FastAPI server for the restaurant recommender system with WebSocket support"""

import asyncio
import json
import uuid
from typing import Optional
from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from runner.orchestrator_runner import OrchestratorRunner


# Pydantic models for request/response
class StartConversationRequest(BaseModel):
    """Request to start a new conversation"""
    user_id: Optional[str] = None
    initial_message: str = "Hi, I'm hungry!"


class MessageRequest(BaseModel):
    """Request to send a message"""
    context_id: str
    user_message: str


class ConversationStateResponse(BaseModel):
    """Response with conversation state"""
    context_id: str
    user_id: str
    energy_level: Optional[int] = None
    budget_level: Optional[int] = None
    group_size: Optional[int] = None
    preferred_cuisine: Optional[str] = None
    search_radius_m: Optional[int] = None
    candidates_count: int = 0
    recommendations_count: int = 0
    selected_restaurant: Optional[dict] = None


# Create FastAPI app
app = FastAPI(
    title="Restaurant Recommender API",
    description="Multi-agent restaurant recommendation system with WebSocket support",
    version="1.0.0"
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global orchestrator instance
orchestrator = OrchestratorRunner()

# Store active WebSocket connections
active_connections = {}


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve a simple HTML interface for testing"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Restaurant Recommender</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                width: 100%;
                max-width: 600px;
                display: flex;
                flex-direction: column;
                height: 80vh;
                max-height: 800px;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 12px 12px 0 0;
                text-align: center;
            }
            .header h1 {
                font-size: 24px;
                margin-bottom: 5px;
            }
            .header p {
                font-size: 14px;
                opacity: 0.9;
            }
            .chat-area {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            .message {
                display: flex;
                animation: slideIn 0.3s ease-out;
            }
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateY(10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
            .message.user {
                justify-content: flex-end;
            }
            .message.assistant {
                justify-content: flex-start;
            }
            .message-content {
                max-width: 70%;
                padding: 12px 16px;
                border-radius: 12px;
                line-height: 1.4;
                font-size: 14px;
            }
            .message.user .message-content {
                background: #667eea;
                color: white;
                border-bottom-right-radius: 4px;
            }
            .message.assistant .message-content {
                background: #f0f0f0;
                color: #333;
                border-bottom-left-radius: 4px;
            }
            .input-area {
                border-top: 1px solid #e0e0e0;
                padding: 15px 20px;
                display: flex;
                gap: 10px;
                background: #fafafa;
                border-radius: 0 0 12px 12px;
            }
            #messageInput {
                flex: 1;
                padding: 10px 15px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
                font-family: inherit;
            }
            #messageInput:focus {
                outline: none;
                border-color: #667eea;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            #sendBtn {
                padding: 10px 20px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 500;
                transition: background 0.2s;
            }
            #sendBtn:hover {
                background: #764ba2;
            }
            #sendBtn:disabled {
                background: #ccc;
                cursor: not-allowed;
            }
            .status {
                font-size: 12px;
                color: #999;
                padding: 10px 20px;
                text-align: center;
            }
            .next-step {
                font-size: 12px;
                color: #667eea;
                font-weight: 500;
                margin-top: 5px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🍽️ Restaurant Recommender</h1>
                <p>Multi-Agent Recommendation System</p>
            </div>
            <div class="chat-area" id="chatArea"></div>
            <div class="status" id="status">Connecting...</div>
            <div class="input-area">
                <input type="text" id="messageInput" placeholder="Type your message...">
                <button id="sendBtn" disabled>Send</button>
            </div>
        </div>

        <script>
            let ws = null;
            let contextId = null;
            let userId = null;

            const chatArea = document.getElementById('chatArea');
            const messageInput = document.getElementById('messageInput');
            const sendBtn = document.getElementById('sendBtn');
            const status = document.getElementById('status');

            function connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                ws = new WebSocket(protocol + '//' + window.location.host + '/ws');

                ws.onopen = () => {
                    status.textContent = 'Connected';
                    sendBtn.disabled = false;
                    startConversation();
                };

                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    handleMessage(data);
                };

                ws.onerror = () => {
                    status.textContent = 'Connection error';
                    sendBtn.disabled = true;
                };

                ws.onclose = () => {
                    status.textContent = 'Disconnected. Reconnecting...';
                    sendBtn.disabled = true;
                    setTimeout(connectWebSocket, 3000);
                };
            }

            function startConversation() {
                ws.send(JSON.stringify({
                    type: 'start',
                    user_id: 'user_' + Math.random().toString(36).substr(2, 9)
                }));
            }

            function handleMessage(data) {
                if (data.type === 'conversation_started') {
                    contextId = data.context_id;
                    userId = data.user_id;
                    addMessage('assistant', data.message);
                    if (data.next_step) {
                        addNextStep(data.next_step);
                    }
                } else if (data.type === 'response') {
                    addMessage('assistant', data.message);
                    if (data.next_step) {
                        addNextStep(data.next_step);
                    }
                    if (data.next_step === 'complete') {
                        showFinalState(data.state);
                    }
                }
            }

            function addMessage(speaker, text) {
                const msgEl = document.createElement('div');
                msgEl.className = 'message ' + speaker;
                const content = document.createElement('div');
                content.className = 'message-content';
                content.textContent = text;
                msgEl.appendChild(content);
                chatArea.appendChild(msgEl);
                chatArea.scrollTop = chatArea.scrollHeight;
            }

            function addNextStep(nextStep) {
                const msgEl = document.createElement('div');
                msgEl.className = 'message assistant';
                const content = document.createElement('div');
                content.className = 'message-content next-step';
                content.textContent = '[Next Step: ' + nextStep + ']';
                msgEl.appendChild(content);
                chatArea.appendChild(msgEl);
                chatArea.scrollTop = chatArea.scrollHeight;
            }

            function showFinalState(state) {
                addMessage('assistant', '\\n📊 Conversation Complete!\\n' +
                    'Selected Restaurant: ' + (state.selected_restaurant?.name || 'None') + '\\n' +
                    'Recommendations: ' + state.recommendations_count);
            }

            function sendMessage() {
                const text = messageInput.value.trim();
                if (!text || !contextId) return;

                addMessage('user', text);
                messageInput.value = '';

                ws.send(JSON.stringify({
                    type: 'message',
                    context_id: contextId,
                    message: text
                }));
            }

            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') sendMessage();
            });

            sendBtn.addEventListener('click', sendMessage);

            connectWebSocket();
        </script>
    </body>
    </html>
    """

@app.post("/chat/start", response_model=dict)
async def start_conversation(request: Optional[StartConversationRequest] = None):
    """Start a new conversation (REST endpoint)"""
    """Start a new conversation (REST endpoint)"""
    user_id = (request.user_id if request else None) or f"user_{uuid.uuid4().hex[:8]}"
    initial_message = (request.initial_message if request else None) or "Hi, I'm hungry!"
    
    try:
        result = await orchestrator.start_conversation(user_id, initial_message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat/message", response_model=dict)
async def send_message(request: MessageRequest):
    """Send a message in an ongoing conversation (REST endpoint)"""
    try:
        result = await orchestrator.process_message(request.context_id, request.user_message)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/state/{context_id}", response_model=dict)
async def get_state(context_id: str):
    """Get current conversation state"""
    try:
        state = orchestrator.state_store.get_state(context_id)
        if not state:
            raise HTTPException(status_code=404, detail="Context not found")
        
        return {
            "context_id": state.context_id,
            "user_id": state.user_id,
            "energy_level": state.energy_level,
            "budget_level": state.budget_level,
            "group_size": state.group_size,
            "preferred_cuisine": state.preferred_cuisine,
            "search_radius_m": state.search_radius_m,
            "candidates_count": len(state.candidates),
            "recommendations_count": len(state.recommendations),
            "selected_restaurant": state.selected_restaurant
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time conversation"""
    await websocket.accept()
    context_id = None
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get('type') == 'start':
                # Start a new conversation
                user_id = message_data.get('user_id', f"user_{uuid.uuid4().hex[:8]}")
                result = await orchestrator.start_conversation(user_id, "Hi, I'm hungry!")
                context_id = result['context_id']
                
                await websocket.send_text(json.dumps({
                    'type': 'conversation_started',
                    'context_id': context_id,
                    'user_id': user_id,
                    'message': result['message'],
                    'next_step': result.get('next_step'),
                    'environment': result.get('environment')
                }))
            
            elif message_data.get('type') == 'message' and context_id:
                # Process user message
                user_message = message_data.get('message')
                result = await orchestrator.process_message(context_id, user_message)
                
                # Get current state
                state = orchestrator.state_store.get_state(context_id)
                state_dict = {
                    'selected_restaurant': state.selected_restaurant if state and hasattr(state, 'selected_restaurant') else None,
                    'recommendations_count': len(state.recommendations) if state and hasattr(state, 'recommendations') else 0
                }
                
                await websocket.send_text(json.dumps({
                    'type': 'response',
                    'message': result.get('message'),
                    'next_step': result.get('next_step'),
                    'state': state_dict
                }))
    
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_text(json.dumps({'type': 'error', 'message': str(e)}))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Restaurant Recommender API",
        "version": "1.0.0"
    }


@app.get("/api/docs", response_class=HTMLResponse)
async def api_docs():
    """Redirect to interactive API documentation"""
    return """
    <html>
        <head>
            <title>API Documentation</title>
            <meta http-equiv="refresh" content="0;url=/docs"/>
        </head>
    </html>
    """


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
