import os
from dotenv import load_dotenv
from snowflake.connector import connect
from snowflake.cortex import Complete
from snowflake.snowpark import Session

# Load environment variables
load_dotenv()

def create_session():
    try:
        connection_parameters = {
            "account": os.getenv('SNOWFLAKE_ACCOUNT'),
            "user": os.getenv('SNOWFLAKE_USER'),
            "password": os.getenv('SNOWFLAKE_PASSWORD'),
            "warehouse": os.getenv('SNOWFLAKE_WAREHOUSE'),
            "database": os.getenv('SNOWFLAKE_DATABASE'),
            "schema": os.getenv('SNOWFLAKE_SCHEMA')
        }
        session = Session.builder.configs(connection_parameters).create()
        print("Session created successfully!")
        return session
    except Exception as e:
        print(f"Session creation failed: {e}")
        return None

def get_relevant_context(query, session):
    try:
        # Using Snowflake's semantic search to find relevant documents
        df = session.sql(f"""
        SELECT content, SIMILARITY_SCORE 
        FROM PARSED_CONTENT
        WHERE VECTOR_SIMILARITY_SEARCH(
            EMBEDDINGS_COLUMN,
            GET_EMBEDDING('{query}')
        )
        ORDER BY SIMILARITY_SCORE DESC
        LIMIT 3
        """).collect()
        
        # Combine the relevant contexts
        context = " ".join([row['CONTENT'] for row in df])
        return context
    except Exception as e:
        print(f"Error retrieving context: {e}")
        return ""

def get_response(prompt):
    session = create_session()
    if not session:
        return "Error: Could not create Snowflake session"
    
    try:
        # First, get relevant context from our knowledge base
        context = get_relevant_context(prompt, session)
        
        # Construct the full prompt with context
        full_prompt = f"""You are an expert with NBCU and know the ins and outs of the company. Your role is to act as a chat support bot that
        will answer any questions, comments, or concerns that the user has regarding NBCU. You don't make random guesses and only answer something if you find
        it in the context. If it is not in the context than you need to state that you do not have that exact information but are making a general guess. Always site the URL/page
        you have aquired this information from and identify whether or not it could be dated.
        
        This is your context: {context}
        
        This is the users question: {prompt}
        
        Now provide an answer:"""
        
        # Use the Cortex SDK to generate response
        response = Complete(
            model="mistral-large2",
            prompt=full_prompt,
            session=session
        )
        
        return response
    except Exception as e:
        return f"Error generating response: {str(e)}"
    finally:
        if session:
            session.close()