import os
from crewai_tools import ZapierActionTools
from crewai import Agent, Task, Crew

zapier_tools = ZapierActionTools()


agent = Agent(
    role="Zapier Agent",
    goal="You are an assistant that can use zapier actions to help me with my tasks",
    backstory="You are a helpful assistant that will help me with zapier actions",
    tools=zapier_tools,
    llm="gpt-4.1-mini",
)

task = Task(
    description="Answer the query using the zapier actions tools. The query is: {query}",
    expected_output="The answer to the query",
    agent=agent,
)

crew = Crew(agents=[agent], tasks=[task], verbose=True)
crew.kickoff(inputs={"query": "Return the most 3 recent emails about zapier events"})
