import yaml
from crewai import LLM, Agent, Crew, Process, Task
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters

try:
    serverparams = StdioServerParameters(
        command="docker",
        args=[
            "run",
            "-i",
            "--rm",
            "-e",
            "GITHUB_PERSONAL_ACCESS_TOKEN",
            "ghcr.io/github/github-mcp-server",
        ],
        env={
            "GITHUB_PERSONAL_ACCESS_TOKEN": "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"
        },
    )
    with MCPServerAdapter(serverparams) as tools:
        ...
        # llm = LLM(
        #     model="gpt-4o-mini",
        #     messages=[
        #         {
        #             "role": "system",
        #             "content": "You are a helpful assistant that will help me create an issue on github, using the github-mcp-server. Auto discover the paramenter and fixes the missing ones",
        #         }
        #     ],
        #     tools=tools,
        # )

        agent = Agent(
            role="Github assistent ",
            goal="create an issue on github",
            backstory="You are a helpful assistant that will help me create an issue on github, using the github-mcp-server",
            verbose=True,
            tools=tools,
        )
        task = Task(
            description="create an issue on github lucasgomide/entregis about package installation",
            expected_output="the issue is created",
            agent=agent,
        )

        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=True,
            process=Process.sequential,
        )

        print(crew.kickoff())

        # output = agent.execute_task(
        #     task,
        #     {
        #         "tool": "create_issue",
        #         "parameters": {
        #             "owner": "lucasgomide",
        #             "repo": "entregis",
        #             "title": "test issue",
        #         },
        #     },
        #     tools,
        # )

        # tools = {
        #     "type": "function",
        #     "name": "create_issue",
        #     "description": "Create an issue on github",
        #     "parameters": {
        #         "owner": {
        #             "type": "string",
        #             "description": "The owner of the repository",
        #         },
        #         "repo": {
        #             "type": "string",
        #             "description": "The name of the repository",
        #         },
        #         "title": {
        #             "type": "string",
        #             "description": "The title of the issue",
        #         },
        #     },
        # }

        # available_functions = {
        #     "create_issue": create_issue,
        # }

        #     "type": "function",
        # "name": "get_weather",
        # "description": "Get current temperature for a given location.",
        # "parameters": {
        #     "type": "object",
        #     "properties": {
        #         "location": {
        #             "type": "string",
        #             "description": "City and country e.g. Bogotá, Colombia"
        #         }
        #     },
        #     "required": [
        #         "location"
        #     ],
        #     "additionalProperties": False
        # }

        # llm = LLM(
        #     model="gpt-4o-mini",
        #     messages=[
        #         {
        #             "role": "system",
        #             "content": "You are a helpful assistant that will help me create an issue on github, using the github-mcp-server. Auto discover the paramenter and fixes the missing ones",
        #         }
        #     ],
        #     available_functions=available_functions,
        # )
        # print(llm.call("create an issue on github, use milestone 1?", tools=tools))


except Exception as e:
    raise Exception(f"An error occurred while running the crew: {e}")
