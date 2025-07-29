#!/usr/bin/env python3
"""
Demo for quick testing TargetAI Token Server
"""

from targetai import TargetAITokenServer

def main():
    print("🎯 TargetAI Token Server - Demo")
    print("=" * 50)
    
    # Settings (change according to your needs)
    # URL can be omitted - https://app.targetai.ai is used by default
    TOS_BASE_URL = None # Leave None to use default URL
    API_KEY = None  # Set your API key or leave None
    HOST = "0.0.0.0"
    PORT = 8001
    
    # Create server
    if TOS_BASE_URL:
        server = TargetAITokenServer(
            tos_base_url=TOS_BASE_URL,
            api_key=API_KEY,
            host=HOST,
            port=PORT
        )
        tos_url_display = TOS_BASE_URL
    else:
        # Use default URL
        server = TargetAITokenServer(
            api_key=API_KEY,
            host=HOST,
            port=PORT
        )
        tos_url_display = "https://app.targetai.ai (default)"
    
    print(f"📡 TOS Backend: {tos_url_display}")
    print(f"🔑 API Key: {'✅ configured' if API_KEY else '❌ not configured (will work without key)'}")
    print(f"🌐 Server: http://{HOST}:{PORT}")
    print()
    
    print("🚀 Starting server...")
    print("📖 Swagger UI will be available at: http://localhost:8001/docs")
    print("🧪 Test commands:")
    print("   curl -X POST http://localhost:8001/token")
    print("   curl http://localhost:8001/health")
    print()
    print("💡 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        server.run()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Make sure that:")
        print("   - TOS backend is accessible at the specified URL")
        print("   - Port 8001 is not occupied by another application")
        print("   - All dependencies are installed: pip install -e .")

if __name__ == "__main__":
    main() 