import os

os.environ["AI_MODE"] = "mock"
os.environ["AI_USE_OPENAI_ANALYSIS"] = "false"
os.environ["AI_USE_OPENAI_REPLY"] = "false"
os.environ["OPENAI_API_KEY"] = ""
os.environ["OPENAI_MODEL"] = "gpt-5.4-mini"
os.environ["OPENAI_MAX_OUTPUT_TOKENS"] = "500"
os.environ["OPENAI_TIMEOUT_SECONDS"] = "30"
