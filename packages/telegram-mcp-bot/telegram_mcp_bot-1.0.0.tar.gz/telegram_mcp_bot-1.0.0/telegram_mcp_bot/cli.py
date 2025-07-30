#!/usr/bin/env python3
"""
Command Line Interface for Telegram MCP Bot
"""

import argparse
import asyncio
import sys
from pathlib import Path

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="telegram-mcp-bot",
        description="Unified Telegram Bot with MCP support"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Demo mode (polling)
    demo_parser = subparsers.add_parser(
        "demo", 
        help="Run bot in demo mode (polling)"
    )
    demo_parser.add_argument(
        "--env-file", 
        default=".env",
        help="Path to environment file"
    )
    
    # Production mode (webhook)
    prod_parser = subparsers.add_parser(
        "prod", 
        help="Run bot in production mode (webhook)"
    )
    prod_parser.add_argument(
        "--env-file",
        default=".env", 
        help="Path to environment file"
    )
    prod_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind webhook server"
    )
    prod_parser.add_argument(
        "--port",
        type=int,
        default=8443,
        help="Port for webhook server"
    )
    
    # Status check
    status_parser = subparsers.add_parser(
        "status",
        help="Check bot status and ChromaDB connection"
    )
    
    # Setup wizard
    setup_parser = subparsers.add_parser(
        "setup",
        help="Interactive setup wizard"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute commands
    if args.command == "demo":
        run_demo_mode(args.env_file)
    elif args.command == "prod":
        run_prod_mode(args.env_file, args.host, args.port)
    elif args.command == "status":
        asyncio.run(check_status())
    elif args.command == "setup":
        run_setup_wizard()

def run_demo_mode(env_file: str):
    """Run bot in demo mode (polling)"""
    print("🚀 Starting Telegram MCP Bot in DEMO mode (polling)")
    print(f"📄 Using environment file: {env_file}")
    
    # Import and run unified bot
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from unified_bot import main as unified_main
    asyncio.run(unified_main())

def run_prod_mode(env_file: str, host: str, port: int):
    """Run bot in production mode (webhook)"""
    print("🚀 Starting Telegram MCP Bot in PRODUCTION mode (webhook)")
    print(f"📄 Using environment file: {env_file}")
    print(f"🌐 Server: {host}:{port}")
    
    # Import and run webhook bot
    from dotenv import load_dotenv
    load_dotenv(env_file)
    
    import os
    os.environ["WEBHOOK_HOST"] = host
    os.environ["WEBHOOK_PORT"] = str(port)
    
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from webhook_bot import main as webhook_main
    asyncio.run(webhook_main())

async def check_status():
    """Check bot status and ChromaDB connection"""
    print("🔍 Checking Telegram MCP Bot status...")
    
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        from check_unified_bot import check_bot_status
        await check_bot_status()
        
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        sys.exit(1)

def run_setup_wizard():
    """Interactive setup wizard"""
    print("🧙 Telegram MCP Bot Setup Wizard")
    print("=" * 40)
    
    env_vars = {}
    
    # Telegram Token
    print("\n📱 Telegram Configuration:")
    token = input("Enter your Telegram Bot Token (from @BotFather): ").strip()
    if not token:
        print("❌ Bot token is required!")
        sys.exit(1)
    env_vars["TELEGRAM_TOKEN"] = token
    
    # LLM API
    print("\n🧠 LLM API Configuration:")
    api_url = input("Enter LLM API Base URL: ").strip()
    if not api_url:
        print("❌ LLM API URL is required!")
        sys.exit(1)
    env_vars["LLM_PROXY_API_BASE_URL"] = api_url
    
    api_key = input("Enter LLM API Key: ").strip()
    if not api_key:
        print("❌ LLM API Key is required!")
        sys.exit(1)
    env_vars["LLM_PROXY_API_KEY"] = api_key
    
    # ChromaDB
    print("\n💾 ChromaDB Configuration:")
    chroma_key = input("Enter OpenAI API Key for ChromaDB embeddings: ").strip()
    if not chroma_key:
        print("❌ ChromaDB API Key is required!")
        sys.exit(1)
    env_vars["CHROMA_OPENAI_API_KEY"] = chroma_key
    
    # Mode selection
    print("\n🚀 Deployment Mode:")
    print("1. Demo mode (polling) - for development and demonstration")
    print("2. Production mode (webhook) - for production servers")
    mode_choice = input("Choose mode (1 or 2): ").strip()
    
    if mode_choice == "1":
        env_vars["DEPLOYMENT_MODE"] = "polling"
        env_vars["PLAYWRIGHT_HEADLESS"] = "false"
    elif mode_choice == "2":
        env_vars["DEPLOYMENT_MODE"] = "webhook"
        env_vars["PLAYWRIGHT_HEADLESS"] = "true"
        
        webhook_host = input("Enter webhook host (your domain): ").strip()
        if webhook_host:
            env_vars["WEBHOOK_HOST"] = webhook_host
        
        webhook_port = input("Enter webhook port (default 8443): ").strip()
        env_vars["WEBHOOK_PORT"] = webhook_port or "8443"
    else:
        print("❌ Invalid choice!")
        sys.exit(1)
    
    # Write .env file
    env_content = []
    env_content.append("# Generated by telegram-mcp-bot setup wizard")
    env_content.append("")
    
    for key, value in env_vars.items():
        env_content.append(f"{key}={value}")
    
    env_content.append("")
    env_content.append("# Additional settings")
    env_content.append("LOG_LEVEL=INFO")
    env_content.append("TOKENIZERS_PARALLELISM=false")
    
    with open(".env", "w") as f:
        f.write("\n".join(env_content))
    
    print("\n✅ Configuration saved to .env")
    print("\n🚀 Ready to start!")
    print("\nFor demo mode: telegram-mcp-bot demo")
    print("For production: telegram-mcp-bot prod")

if __name__ == "__main__":
    main() 