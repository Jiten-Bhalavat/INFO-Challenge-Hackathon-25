import streamlit as st
from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

def initialize_graph():
    return Neo4jGraph(
        url=os.getenv('NEO4J_URI'),
        username=os.getenv('NEO4J_USERNAME'),
        password=os.getenv('NEO4J_PASSWORD')
    )

def initialize_llm():
    return ChatGroq(groq_api_key=os.environ["GROQ_API_KEY"], model_name="mixtral-8x7b-32768")

def create_cypher_chain(llm, graph):
    CYPHER_GENERATION_TEMPLATE = """Task:Generate Cypher statement to query a graph database.
    Instructions:
    Use only the provided relationship types and properties in the schema.
    Do not use any other relationship types or properties that are not provided.
    Only include the generated Cypher statement in your response.
    start the cypher command with match


    Always use case insensitive search when matching strings.

    Schema:
    {schema}

    The question is:
    {question}"""

    cypher_generation_prompt = PromptTemplate(
        template=CYPHER_GENERATION_TEMPLATE,
        input_variables=["schema", "question"],
    )
    
    return GraphCypherQAChain.from_llm(
        llm,
        graph=graph,
        cypher_prompt=cypher_generation_prompt,
        verbose=True,
        allow_dangerous_requests=True
    )

def run_cypher(chain, q):
    return chain.invoke({"query": q}, verbose=True)

def main():
    load_dotenv("key.env")
    
    graph = initialize_graph()
    llm = initialize_llm()
    cypher_chain = create_cypher_chain(llm, graph)
    
    st.title("Neo4j Graph Query Interface")
    st.write("Enter a question to generate and run a Cypher query on the Neo4j database.")
    
    query = st.text_input("Enter your query:")
    if st.button("Run Query"):
        if query:
            response = run_cypher(cypher_chain, query)
            st.subheader("Query Result:")
            st.write(response)
        else:
            st.error("Please enter a query before running.")

if __name__ == "__main__":
    main()
