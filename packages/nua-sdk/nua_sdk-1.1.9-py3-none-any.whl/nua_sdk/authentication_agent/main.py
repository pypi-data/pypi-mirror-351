import os
from langgraph_sdk import get_sync_client
from dotenv import load_dotenv

load_dotenv()


class AuthenticationAgent:
    def __init__(self, message: str):
        self.auth_agent = get_sync_client(url=os.getenv("AUTH_AGENT_URL"))
        self.message = message
    
    def authenticate(self):
        session_details = None
        error_message = None
        
        try:
            # Create thread
            thread_response = self.auth_agent.threads.create()
            if not thread_response or not isinstance(thread_response, dict):
                print("❌ Failed to create thread - invalid response from auth agent")
                return None
                
            thread_id = thread_response.get("thread_id")
            if not thread_id:
                print("❌ Failed to get thread_id from auth agent response")
                return None
            
            print(f"🔧 Created thread: {thread_id}")
            
            # Start streaming response
            response = self.auth_agent.runs.stream(
                thread_id=thread_id,
                assistant_id="auth_agent",
                input={
                    "messages": [{"role": "user", "content": self.message}]
                },
                stream_mode="values"
            )
            
            print("📡 Starting to process streaming response...")
            
            # Process streaming chunks with proper error handling
            chunk_count = 0
            for chunk in response:
                chunk_count += 1
                try:
                    # Check if chunk has data attribute and it's not None
                    if hasattr(chunk, 'data') and chunk.data is not None:
                        print(f"📦 Chunk {chunk_count}: Found data attribute")
                        
                        # Safely check for session_details
                        if isinstance(chunk.data, dict):
                            print(f"📊 Chunk {chunk_count}: Data is dict with keys: {list(chunk.data.keys())}")
                            
                            if chunk.data.get("session_details") is not None:
                                session_details = chunk.data.get("session_details")
                                print(f"✅ Received session details from auth agent")
                                break
                            
                            # Check for error response
                            if chunk.data.get("error") is not None:
                                error_message = chunk.data.get("message", "Unknown error")
                                print(f"❌ Auth agent reported error: {error_message}")
                                break
                        else:
                            print(f"📊 Chunk {chunk_count}: Data is {type(chunk.data)}: {chunk.data}")
                    else:
                        # chunk.data is None or chunk doesn't have data attribute
                        # This is normal during streaming, just continue
                        continue
                        
                except Exception as chunk_error:
                    print(f"⚠️  Error processing chunk {chunk_count}: {chunk_error}")
                    continue
                    
            print(f"📊 Processed {chunk_count} chunks total")
            
        except Exception as e:
            print(f"❌ Error during authentication streaming: {e}")
            import traceback
            traceback.print_exc()
            return None
            
        # Handle error responses
        if error_message:
            print(f"💡 Authentication failed due to: {error_message}")
            return None
            
        if session_details:
            # Check if session_details contains an error
            if isinstance(session_details, str):
                if session_details.startswith("ERROR"):
                    if "Expecting value: line 1 column 1" in session_details:
                        print(f"❌ Website authentication failed: Target website returned empty/invalid response")
                        print(f"💡 This often means:")
                        print(f"   • The target website is down or inaccessible")
                        print(f"   • The login credentials are incorrect")
                        print(f"   • The login page URL has changed")
                        print(f"   • The website requires different authentication flow")
                    else:
                        print(f"❌ Auth agent returned error: {session_details}")
                    return None
                else:
                    # String response that's not an error - this shouldn't happen
                    print(f"⚠️  Unexpected string response: {session_details}")
                    return None
                    
        return session_details