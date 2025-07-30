# LiveKit Plugins Dify

Agent Framework plugin for Dify.

## Installation
```python
pip install livekit-plugins-dify
```

## Pre-requisites

- Dify API Key environment variables: `DIFY_API_KEY`

## Usage


This example shows how to use the Dify plugin.

```python
from livekit.agents import Agent, AgentSession, JobContext, cli, WorkerOptions
from livekit.plugins import dify
from dotenv import load_dotenv


async def entry_point(ctx: JobContext):
    
    await ctx.connect()
    
    agent = Agent(instructions="You are a helpful assistant.")

    session = AgentSession(
        llm = dify.LLM(user="xxx")
    )
    
    await session.start(agent=agent, room=ctx.room)


if __name__ == "__main__":
    load_dotenv()
    cli.run_app(WorkerOptions(entrypoint_fnc=entry_point))
```

