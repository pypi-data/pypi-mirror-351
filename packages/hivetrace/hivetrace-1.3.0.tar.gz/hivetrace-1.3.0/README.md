# Hivetrace SDK

## Overview

Hivetrace SDK is designed for integration with the Hivetrace service, providing monitoring of user prompts and LLM responses.

## Installation

Install the SDK via pip:

```bash
pip install hivetrace
```

## Usage

```python
from hivetrace.hivetrace import HivetraceSDK
```

## Synchronous and Asynchronous Modes

Hivetrace SDK supports both synchronous and asynchronous execution modes. By default, it operates in asynchronous mode. You can specify the mode explicitly during initialization.

### Sync Mode

#### Sync Mode Initialization

```python
# Sync mode
hivetrace = HivetraceSDK(async_mode=False)
```

#### Sending a User Prompt

```python
# Sync mode
response = hivetrace.input(
    application_id="your-application-id",  # obtained after registering the application in the UI
    message="User prompt here"
)
```

#### Sending LLM Response

```python
# Sync mode
response = hivetrace.output(
    application_id="your-application-id",  # obtained after registering the application in the UI
    message="LLM response here"
)
```

### Async Mode

#### Async Mode Initialization

```python
# Async mode (default)
hivetrace = HivetraceSDK(async_mode=True)
```

#### Sending a User Prompt

```python
# Async mode
response = await hivetrace.input_async(
    application_id="your-application-id",  # obtained after registering the application in the UI
    message="User prompt here"
)
```

#### Sending LLM Response

```python
# Async mode
response = await hivetrace.output_async(
    application_id="your-application-id",  # obtained after registering the application in the UI
    message="LLM response here"
)
```

## Example with Additional Parameters

```python
response = hivetrace.input(
    application_id="your-application-id", 
    message="User prompt here",
    additional_parameters={
        "session_id": "your-session-id",
        "user_id": "your-user-id",
        "agents": {
            "agent-1-id": {"name": "Agent 1", "description": "Agent description"},
            "agent-2-id": {"name": "Agent 2"},
            "agent-3-id": {}
        }
    }
)
```

> **Note:** `session_id`, `user_id`, and `agent_id` must be valid UUIDs.

## API

### `input`

```python
def input(application_id: str, message: str, additional_parameters: dict = None) -> dict:
    ...
```

Sends a user prompt to Hivetrace.

* `application_id`: Application identifier (must be a valid UUID, created in the UI)
* `message`: User prompt
* `additional_parameters`: Dictionary of additional parameters (optional)

**Response Example:**

```json
{
    "status": "processed",
    "monitoring_result": {
        "is_toxic": false,
        "type_of_violation": "benign",
        "token_count": 9,
        "token_usage_warning": false,
        "token_usage_unbounded": false
    }
}
```

### `output`

```python
def output(application_id: str, message: str, additional_parameters: dict = None) -> dict:
    ...
```

Sends an LLM response to Hivetrace.

* `application_id`: Application identifier (must be a valid UUID, created in the UI)
* `message`: LLM response
* `additional_parameters`: Dictionary of additional parameters (optional)

**Response Example:**

```json
{
    "status": "processed",
    "monitoring_result": {
        "is_toxic": false,
        "type_of_violation": "safe",
        "token_count": 21,
        "token_usage_warning": false,
        "token_usage_unbounded": false
    }
}
```

## Sending Requests in Sync Mode

```python
def main():
    hivetrace = HivetraceSDK(async_mode=False)
    response = hivetrace.input(
        application_id="your-application-id",
        message="User prompt here"
    )

main()
```

## Sending Requests in Async Mode

```python
import asyncio

async def main():
    hivetrace = HivetraceSDK(async_mode=True)
    response = await hivetrace.input_async(
        application_id="your-application-id",
        message="User prompt here"
    )
    await hivetrace.close()

asyncio.run(main())
```

### Closing the Async Client

```python
await hivetrace.close()
```

## Configuration

The SDK loads configuration from environment variables. The allowed domain (`HIVETRACE_URL`) and API token (`HIVETRACE_ACCESS_TOKEN`) are automatically retrieved from the environment.

### Configuration Sources

Hivetrace SDK can retrieve configuration from the following sources:

**.env File:**

```bash
HIVETRACE_URL=https://your-hivetrace-instance.com
HIVETRACE_ACCESS_TOKEN=your-access-token  # obtained in the UI (API Tokens page)
```

The SDK will automatically load these settings.

You can also use the config when initializing an instance of the havetrace sdk class to load settings.
```bash
trace = HivetraceSDK(
        config={
            "HIVETRACE_URL": HIVETRACE_URL,
            "HIVETRACE_ACCESS_TOKEN": HIVETRACE_ACCESS_TOKEN,
        },
        async_mode=False,
    )
```

# Monitoring Agent Systems with HiveTrace SDK

## CrewAI Integration

Monitor your multi-agent CrewAI systems with automatic tracking of all agent interactions, tool usage, and task executions.

> **Important**: This integration is designed for **linear agent workflows** where agents execute tasks sequentially. Coming soon: Support for complex agent interaction models (parallel execution, dynamic delegation).
> 
> **Note**: The agents shown in examples (Researcher, Writer, Reviewer) are for demonstration purposes only. You can use any agents with any roles, goals, and tools that fit your specific use case.

---

## Quick Start

### Prerequisites

- HiveTrace SDK installed: `pip install hivetrace`
- Valid HiveTrace application ID and access token

### Basic Setup

**Step 1: # Initialize the SDK (required) - use .env or config**

```python
from hivetrace import HivetraceSDK

# Initialize SDK (required)
hivetrace = HivetraceSDK(
    config={
        "HIVETRACE_URL": "https://your-hivetrace-instance.com",      # required
        "HIVETRACE_ACCESS_TOKEN": "your-access-token",              # required
    },
    async_mode=False,  # optional, default=True
)
```

**Step 2: Configure Agent Monitoring**

```python
import uuid
from crewai import Agent, Crew, Task
from hivetrace.crewai_adapter import trace

# Create unique UUIDs for your agents (generate once and store)
RESEARCHER_ID = str(uuid.uuid4())
WRITER_ID = str(uuid.uuid4())
REVIEWER_ID = str(uuid.uuid4())

# Define agent identifiers (required for monitoring)
AGENT_IDS = {
    "researcher": RESEARCHER_ID,
    "writer": WRITER_ID,
    "reviewer": REVIEWER_ID,
}

# Create agent mapping for monitoring (required)
agent_id_mapping = {
    "Researcher": {
        "id": AGENT_IDS["researcher"], 
        "description": "Researches topics and gathers information"
    },
    "Writer": {
        "id": AGENT_IDS["writer"], 
        "description": "Creates high-quality written content"
    },
    "Reviewer": {
        "id": AGENT_IDS["reviewer"], 
        "description": "Reviews and improves content quality"
    },
}
```

**Step 3: Set Up Agents with Tool Tracking**

```python
from crewai_tools import WebSearchTool

# Create tools and assign agent IDs for tracking
research_tools = [WebSearchTool()]
for tool in research_tools:
    tool.agent_id = AGENT_IDS["researcher"]  # required for tool tracking

# Define agents
researcher = Agent(
    role="Researcher",
    goal="Research the given topic thoroughly",
    backstory="Expert researcher with access to web search",
    tools=research_tools,
    verbose=True,
)

writer = Agent(
    role="Writer", 
    goal="Write comprehensive content",
    backstory="Professional content writer",
    verbose=True,
)

reviewer = Agent(
    role="Reviewer",
    goal="Review and improve content quality", 
    backstory="Editorial expert focused on quality",
    verbose=True,
)
```

**Step 4: Apply Monitoring Decorator**

```python
@trace(
    hivetrace=hivetrace,                           # required
    application_id="your-hivetrace-app-id",       # required
    agent_id_mapping=agent_id_mapping,            # required
)
def create_monitored_crew():
    """Create and return a monitored CrewAI crew."""
    
    # Define tasks
    research_task = Task(
        description="Research {topic} and gather key information",
        agent=researcher,
        expected_output="Detailed research report"
    )
    
    writing_task = Task(
        description="Write article about {topic} based on research",
        agent=writer,
        expected_output="Well-written article"
    )
    
    review_task = Task(
        description="Review and improve the article",
        agent=reviewer, 
        expected_output="Polished final article"
    )
    
    return Crew(
        agents=[researcher, writer, reviewer],
        tasks=[research_task, writing_task, review_task],
        verbose=True,
    )
```

**Step 5: Execute with Monitoring**

    # Note: All parameters in additional_parameters are optional, 
    # but the "agents" parameter is required if you want to monitor agent activities

```python
def run_monitored_workflow(topic: str, user_id: str = None, session_id: str = None):
    """Execute the agent workflow with full monitoring."""
    
    # Generate conversation ID for this execution
    conversation_id = str(uuid.uuid4())
    
    # Log initial user input (recommended)
    hivetrace.input(
        application_id="your-hivetrace-app-id",
        message=f"User requested content creation for topic: {topic}",
        additional_parameters={
            "agent_conversation_id": conversation_id,
            "user_id": user_id,                    # optional
            "session_id": session_id,              # optional
            "agents": {
                agent_data["id"]: {
                    "name": agent_name,
                    "description": agent_data["description"]
                }
                for agent_name, agent_data in agent_id_mapping.items()
            }
        },
    )
    
    # Create and execute crew
    crew = create_monitored_crew()
    
    # Execute with runtime parameters
    execution_params = {"inputs": {"topic": topic}}
    if user_id:
        execution_params["user_id"] = user_id
    if session_id:
        execution_params["session_id"] = session_id
    if conversation_id:
        execution_params["agent_conversation_id"] = conversation_id
        
    result = crew.kickoff(**execution_params)
    return result
```

---

## Configuration Reference

### Required Parameters

| Parameter | Description |
|-----------|-------------|
| `hivetrace` | Initialized SDK instance |
| `application_id` | Your HiveTrace application ID from UI |
| `agent_id_mapping` | Mapping of agent roles to IDs and descriptions |

### Optional Parameters

| Parameter | Description |
|-----------|-------------|
| `user_id` | User identifier |
| `session_id` | Session identifier |

### Agent ID Mapping Format

```python
agent_id_mapping = {
    "Agent Role Name": {
        "id": "unique-uuid-string",           # required
        "description": "Agent description"    # required
    }
}
```

---

## Environment Variables

Set up your environment variables for easier configuration:

```bash
# .env file
HIVETRACE_URL=https://your-hivetrace-instance.com
HIVETRACE_ACCESS_TOKEN=your-access-token
HIVETRACE_APP_ID=your-application-id
```

```python
import os
from dotenv import load_dotenv

load_dotenv()

hivetrace = HivetraceSDK(
    config={
        "HIVETRACE_URL": os.getenv("HIVETRACE_URL"),
        "HIVETRACE_ACCESS_TOKEN": os.getenv("HIVETRACE_ACCESS_TOKEN"),
    },
    async_mode=False,
)
```

---

## Advanced Usage

### Async Mode

```python
import asyncio

# Initialize in async mode
hivetrace = HivetraceSDK(async_mode=True)

@trace(hivetrace=hivetrace, application_id="app-id", agent_id_mapping=mapping)
def create_crew():
    return Crew(agents=[...], tasks=[...])

async def run_async_workflow():
    # Log user input
    await hivetrace.input_async(
        application_id="app-id",
        message="User input",
    )
    
    # Execute crew (requires CrewAI with async support)
    crew = create_crew()
    result = await crew.kickoff_async(inputs={"topic": "AI"})
    
    # Don't forget to close async client
    await hivetrace.close()

# Run async workflow
asyncio.run(run_async_workflow())
```

### Tool Tracking

For comprehensive monitoring, assign agent IDs to all tools:

```python
from crewai_tools import FileReadTool, WebSearchTool

# Create tools
search_tool = WebSearchTool()
file_tool = FileReadTool()

# Assign agent ID for tracking (required)
search_tool.agent_id = "agent-uuid-here"
file_tool.agent_id = "agent-uuid-here"

# Add to agent
agent = Agent(
    role="Researcher",
    tools=[search_tool, file_tool],
    # ... other parameters
)
```

---

You now have complete monitoring of your CrewAI agent system integrated with HiveTrace!

## License
This project is licensed under the Apache License 2.0.