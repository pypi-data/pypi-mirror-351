from nl2sql import NL2SQL

# Using context manager (recommended)
with NL2SQL(
    database_url="sqlite:///test.db",
    llm_provider="cohere",
    api_key="Fl3ViyMPzd6zldSPcDgWiq4Y866MLDxeGgOQgy5x"
) as nl2sql:
    
    # Simple query
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