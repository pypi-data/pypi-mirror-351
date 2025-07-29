#!/usr/bin/env python3
"""
Test script for the NL2SQL package.
Make sure you have set up your .env file with API keys before running.
"""
import os
from dotenv import load_dotenv
from nl2sql import NL2SQL

# Load environment variables
load_dotenv()

def test_basic_functionality():
    """Test basic NL2SQL functionality."""
    
    print("🚀 Testing NL2SQL Package")
    print("=" * 50)
    
    # Check if API key is available
    openai_key = os.getenv("OPENAI_API_KEY")
    cohere_key = os.getenv("COHERE_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not any([openai_key, cohere_key, anthropic_key]):
        print("❌ Error: No API keys found in .env file!")
        print("Please add at least one API key to your .env file:")
        print("OPENAI_API_KEY=your-key-here")
        print("COHERE_API_KEY=your-key-here")
        print("ANTHROPIC_API_KEY=your-key-here")
        return
    
    # Choose provider based on available keys
    if openai_key:
        provider = "openai"
        api_key = openai_key
        print(f"✅ Using OpenAI provider")
    elif cohere_key:
        provider = "cohere" 
        api_key = cohere_key
        print(f"✅ Using Cohere provider")
    elif anthropic_key:
        provider = "anthropic"
        api_key = anthropic_key
        print(f"✅ Using Anthropic provider")
    
    # Database connection
    database_url = "sqlite:///test.db"
    
    try:
        # Initialize NL2SQL
        with NL2SQL(
            database_url=database_url,
            llm_provider=provider,
            api_key=api_key,
            model="gpt-4o" if provider == "openai" else None
        ) as nl2sql:
            
            print(f"✅ Connected to database successfully")
            
            # Test 1: Show available tables
            print("\n" + "="*50)
            print("📋 TEST 1: Available Tables")
            tables = nl2sql.get_tables()
            print(f"Tables in database: {tables}")
            
            # Test 2: Simple query
            print("\n" + "="*50)
            print("🔍 TEST 2: Simple Query")
            question = "Show me all customers from Texas"
            print(f"Question: {question}")
            
            result = nl2sql.ask(question)
            
            print(f"Generated SQL: {result['sql_query']}")
            
            if result['error']:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Query executed successfully!")
                print(f"Results shape: {result['results'].shape}")
                print(f"Results:\n{result['results']}")
            
            # Test 3: Query with explanation
            print("\n" + "="*50)
            print("📊 TEST 3: Query with Explanation")
            question = "What are the top 5 most expensive products?"
            print(f"Question: {question}")
            
            result = nl2sql.ask(question, explain=True)
            
            print(f"Generated SQL: {result['sql_query']}")
            print(f"Explanation: {result['explanation']}")
            
            if result['error']:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Query executed successfully!")
                print(f"Results:\n{result['results']}")
            
            # Test 4: Aggregation query
            print("\n" + "="*50)
            print("📈 TEST 4: Aggregation Query")
            question = "How many orders has each customer made?"
            print(f"Question: {question}")
            
            result = nl2sql.ask(question)
            
            print(f"Generated SQL: {result['sql_query']}")
            
            if result['error']:
                print(f"❌ Error: {result['error']}")
            else:
                print(f"✅ Query executed successfully!")
                print(f"Results:\n{result['results']}")
            
            # Test 5: Schema information
            print("\n" + "="*50)
            print("🗄️  TEST 5: Schema Information")
            schema_info = nl2sql.get_schema_info()
            print("Database Schema (first 500 characters):")
            print(schema_info[:500] + "..." if len(schema_info) > 500 else schema_info)
            
            print("\n" + "="*50)
            print("🎉 All tests completed successfully!")
            
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure test.db exists (run create_test_db.py)")
        print("2. Check your API key in .env file")
        print("3. Ensure all dependencies are installed")

def test_different_questions():
    """Test with various types of questions."""
    
    questions = [
        "Show me customers who signed up in 2023",
        "What's the total revenue from completed orders?",
        "Which product category has the highest average price?",
        "List customers who have never placed an order",
        "What are the monthly sales trends?",
        "Show me orders with more than 2 items",
    ]
    
    print("\n" + "="*60)
    print("🧪 TESTING VARIOUS QUESTION TYPES")
    print("="*60)
    
    # Use first available API key
    openai_key = os.getenv("OPENAI_API_KEY")
    cohere_key = os.getenv("COHERE_API_KEY") 
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    if openai_key:
        provider, api_key = "openai", openai_key
    elif cohere_key:
        provider, api_key = "cohere", cohere_key
    elif anthropic_key:
        provider, api_key = "anthropic", anthropic_key
    else:
        print("❌ No API keys available")
        return
    
    try:
        with NL2SQL(
            database_url="sqlite:///test.db",
            llm_provider=provider,
            api_key=api_key
        ) as nl2sql:
            
            for i, question in enumerate(questions, 1):
                print(f"\n--- Question {i} ---")
                print(f"Q: {question}")
                
                result = nl2sql.ask(question, execute=False)  # Just generate SQL
                
                if result['error']:
                    print(f"❌ Error: {result['error']}")
                else:
                    print(f"SQL: {result['sql_query']}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_basic_functionality()
    test_different_questions()