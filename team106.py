# imports the BigQuery Python Client Library  
from google.cloud import bigquery
import pandas as pd
import streamlit as st
import langchain
import vertexai
from google.cloud import aiplatform
from langchain.llms import VertexAI
from langchain.document_loaders import BigQueryLoader
from langchain.prompts import PromptTemplate
from langchain.schema import format_document

#initializes a BigQuery client. 
# The BigQuery client will be used to send and receive messages from the BigQuery API.
client = bigquery.Client()
# does this need to be installed/run separately as a prerequisite for setting up the python environment(?)

#You will need to initialize vertexai with your project_id and location:
PROJECT_ID = "formula-e-shared24lon-123"
LOCATION = "us-west1"
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Define our query
# specifically targeting meta data of the tables involved
# this pulls back all of the metadata for the tables in the database in question
# which the 'chain' object can use to help the model generate queries from english language statements
query = f"""
SELECT table_name, ddl
FROM `formula-e-shared24lon-123.fe_hackathon_ldn_24.INFORMATION_SCHEMA.TABLES`
WHERE table_type = 'BASE TABLE'
ORDER BY table_name;
"""
# Load the data
loader = BigQueryLoader(
    query, metadata_columns="table_name", page_content_columns="ddl"
)
# create a 'load' object from the BigQueryLoader function
data = loader.load()

# Use code generation model
#llm = VertexAI(model_name="code-bison@latest", max_output_tokens=2048)
llm = VertexAI(
    model="gemini-1.5-flash-001",
    temperature=1,
    max_tokens=None,
    max_retries=6,
    stop=None,
    # other params...
)

# we will get the prompt specific input from a streamlit input box
#issue = st.text_input("Enter the medical issue description:")
#'querypromptcontent  = "help me count bike journeys by start location"


def runquery(querypromptcontent_var):
    # Define the chain
    chain = (
    {
        "content": lambda docs: "\n\n".join(
            format_document(doc, PromptTemplate.from_template("{page_content}"))
            for doc in docs
        )
    }
    | PromptTemplate.from_template(
        f"""Suggest a GoogleSQL query to {querypromptcontent_var}:\n\n{{content}}"""
    )
    | llm
    )
    # Invoke the chain with the documents, and remove code backticks
    # chain object (combination of user prompt and llm model) uses metadata to dynamically create query
    generatedquery = chain.invoke(data).strip("```")
    generatedquery = generatedquery[7:10000]
    df2 = client.query(generatedquery).to_dataframe()
    return df2



# Streamlit app interface
st.title("Query the Formula E Telemetry Data")

querypromptcontent = st.text_input("Please enter your query about the formula E race:")

if st.button("Run Query"):
    if querypromptcontent:
        Qdataframe = runquery(querypromptcontent)
        # Display the dataframe for reference
        st.write("The Result of Your Query:")
        st.dataframe(Qdataframe)
    else:
        st.write("Please enter a valid query about Formula E.")
        
        # Ensure Streamlit listens on the correct port
if __name__ == '__main__':
    st._is_running_with_streamlit = True
    from streamlit.cli import main
    main(prog_name='streamlit', args=['run', 'team106.py', '--server.port=8080'])



