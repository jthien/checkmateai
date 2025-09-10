PROJECT_ID = "vodaf-hack25dus-903"  # @param {type:"string"}
LOCATION = "us-central1"  # @param {type:"string"}
STAGING_BUCKET = "gs://staging-hack-903"  # @param {type:"string"}

import vertexai

vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

from vertexai import agent_engines
from vertexai.preview.reasoning_engines import LangchainAgent

# Define a function for the Agent
def get_exchange_rate(
    currency_from: str = "USD",
    currency_to: str = "EUR",
    currency_date: str = "latest",
):
    """Retrieves the exchange rate between two currencies on a specified date."""
    import requests

    response = requests.get(
        f"https://api.frankfurter.app/{currency_date}",
        params={"from": currency_from, "to": currency_to},
    )
    return response.json()
  
# Test the function
get_exchange_rate(currency_from="USD", currency_to="SEK")


# Install missing packages in VertexAI Workbench to test the agent.
# It is not needed if we install the agent directly in Agent Engine
# Run on local machine
# %pip install --upgrade --quiet \
#     "google-cloud-aiplatform[agent_engines,langchain]" \
#     cloudpickle==3.0.0 \
#     "pydantic>=2.10" \
#     requests

model = "gemini-2.5-pro"
agent = LangchainAgent(
    model=model,
    tools=[get_exchange_rate],
    agent_executor_kwargs={"return_intermediate_steps": True},
)

# Test the agent
agent.query(input="What's the exchange rate from US dollars to Swedish currency today?")

# Install agent in Vertex AI Agent Engine
agent = LangchainAgent(
    model=model,
    tools=[get_exchange_rate],
)

remote_agent = agent_engines.create(
    agent,
    display_name="CheckMetaAI-Simple-Demo-Agent",
    requirements=[
        "google-cloud-aiplatform[agent_engines,langchain]",
        "cloudpickle==3.0.0",
        "pydantic>=2.10",
        "requests",
    ],
)
