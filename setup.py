"""Setup script for Financial GraphRAG system."""

import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}\n")

    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}:")
        print(e.stderr if e.stderr else str(e))
        return False


def check_python_version():
    """Check if Python version is 3.11+"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✅ Python {version.major}.{version.minor} detected")
        return True
    else:
        print(f"❌ Python 3.11+ required. Current: {version.major}.{version.minor}")
        return False


def main():
    """Main setup script."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     Financial GraphRAG System - Setup Script               ║
║                                                              ║
║     Real-Time Financial Intelligence with GraphRAG          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

    # Check Python version
    if not check_python_version():
        sys.exit(1)

    # Install dependencies
    if not run_command(
        "pip install -r requirements.txt",
        "Installing Python dependencies"
    ):
        print("\n⚠️ Some dependencies may have failed to install.")
        print("You may need to install them manually.")

    # Download spaCy model
    if not run_command(
        "python -m spacy download en_core_web_sm",
        "Downloading spaCy language model"
    ):
        print("\n⚠️ spaCy model download failed. Please install manually:")
        print("   python -m spacy download en_core_web_sm")

    # Create .env file if it doesn't exist
    env_file = Path(".env")
    env_example = Path("config/.env.example")

    if not env_file.exists():
        if env_example.exists():
            print("\n📝 Creating .env file from template...")
            with open(env_example) as f:
                content = f.read()
            with open(env_file, 'w') as f:
                f.write(content)
            print("✅ .env file created. Please configure your API keys!")
        else:
            print("⚠️ .env.example not found. Please create .env manually.")
    else:
        print("✅ .env file already exists")

    # Check Neo4j
    print("\n" + "="*60)
    print("🗄️ Neo4j Database Setup")
    print("="*60)
    print("""
Neo4j is required for the knowledge graph. You have two options:

Option 1: Neo4j Desktop (Recommended for beginners)
- Download from: https://neo4j.com/download/
- Install and create a new database
- Set a password and update it in .env file

Option 2: Docker
- Run: docker run -d --name neo4j \\
        -p 7474:7474 -p 7687:7687 \\
        -e NEO4J_AUTH=neo4j/your_password \\
        neo4j:latest
- Update password in .env file

After setting up Neo4j, verify it's running at: http://localhost:7474
""")

    # API Keys reminder
    print("\n" + "="*60)
    print("🔑 API Keys Configuration")
    print("="*60)
    print("""
Please obtain and configure the following API keys in your .env file:

REQUIRED:
1. Neo4j Password - From your Neo4j setup
2. LLM API Key - Choose ONE:
   - OpenAI API Key: https://platform.openai.com/api-keys
   - Anthropic API Key: https://console.anthropic.com/

OPTIONAL (for full functionality):
3. Finnhub API Key: https://finnhub.io/register (Free tier available)
4. NewsAPI Key: https://newsapi.org/register (Free tier available)
5. Reddit API: https://www.reddit.com/prefs/apps (Optional)

Edit the .env file and add your keys!
""")

    # Final instructions
    print("\n" + "="*60)
    print("🚀 Next Steps")
    print("="*60)
    print("""
1. Configure your .env file with API keys
2. Start Neo4j database
3. Run the application:

   streamlit run src/ui/app.py

4. Open your browser at: http://localhost:8501
5. Click "Refresh Data" to populate the knowledge graph
6. Start asking questions in the AI Assistant!

For detailed documentation, see README.md

Happy analyzing! 📊🚀
""")

    print("="*60)
    print("Setup script completed!")
    print("="*60)


if __name__ == "__main__":
    main()
