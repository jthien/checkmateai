#It may not work it automatically 
### to run set the follwoing vairable
# If using Gemini via Vertex AI on Google CLoud
# GOOGLE_CLOUD_PROJECT="your-project-id"
# GOOGLE_CLOUD_LOCATION="your-location" #e.g. us-central1
# GOOGLE_GENAI_USE_VERTEXAI="True"
# https://cloud.google.com/vertex-ai/generative-ai/docs/agent-development-kit/quickstart?hl=en
# the init file will look: from . import check-agent

import os
import re
import datetime
from typing import Optional
from zoneinfo import ZoneInfo

# ADK core
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext

# Google Gen AI SDK (official)
from google import genai
from google.genai import types as genai_types

# ---------------------------------------------------------------------
# Utility tools you already had
# ---------------------------------------------------------------------


# ---------------------------------------------------------------------
# SQL style checker (file reader + prompt builder + SQL detection)
# ---------------------------------------------------------------------
def _read_style_guide() -> str:
    """Load style_guide.txt that lives alongside this file."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    style_guide_path = os.path.join(current_dir, "style_guide.txt")
    with open(style_guide_path, "r", encoding="utf-8") as f:
        return f.read()


# ---------------------------------------------------------------------
# BEFORE-AGENT CALLBACK: intercept SQL and return a content override
# ---------------------------------------------------------------------
def sql_style_before_agent(callback_context: CallbackContext) -> Optional[genai_types.Content]:
    """
    If the latest user message contains SQL, run the style check here and
    return a Content override. Otherwise, return None to let the agent proceed.
    """


    # 3) Load the local style guide
    try:
        style_guide_text = _read_style_guide()
    except FileNotFoundError:
        # Return a friendly model-content explaining the missing file.
        msg = (
            "⚠️ **Style guide file not found.**\n"
            "Please add `style_guide.txt` next to your Python module, then try again."
        )
        return genai_types.Content(role="model", parts=[genai_types.Part.from_text(msg)])

    # 4) Build the style-check prompt
    #prompt = _build_style_prompt(style_guide_text, sql_code)
    callback_context.state["style_guide_text"]=style_guide_text

    return None

instruction="""
You are an expert SQL style checker. Analyze the following SQL code against the Vodafone provided style guide.

--- Style Guide ---
{style_guide_text}

--- Analysis ---
Identify and explain any violations of the style guide. If the code is compliant, state that it follows all rules.
Return a concise, structured report with:
- Summary
- Violations (numbered, with rule references)
- Suggested fixes (diffs or corrected snippets where useful)
- Overall verdict (Compliant / Needs changes)
    """

# ---------------------------------------------------------------------
# Root agent
# ---------------------------------------------------------------------
root_agent = Agent(
    name="sql_checker_agent",
    model="gemini-2.0-flash",
    description="Agent to check SQL code against a style guide.",
    instruction=instruction,
    before_agent_callback=sql_style_before_agent,  # <-- wire-in the callback
)