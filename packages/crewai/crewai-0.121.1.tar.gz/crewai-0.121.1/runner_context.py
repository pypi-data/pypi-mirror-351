from crewai import Agent, Crew, Task

agent = Agent(
    role="Random Name Generator",
    goal="Generate a random name",
    backstory="You are a helpful assistant that can generate random names.",
)

task = Task(
    description="Generate a random name",
    expected_output="A random name",
    agent=agent,
)

agent2 = Agent(
    role="Random Name Generator",
    goal="Generate a random name",
    backstory="You are a helpful assistant that can generate random names.",
)
task2 = Task(
    description="Generate a random number",
    expected_output="A random number",
    agent=agent2,
    context=[],
)

agent3 = Agent(
    role="Agrigator",
    goal="Aggregate the results of the other agents",
    backstory="You are a helpful assistant that can aggregate the results of the other agents.",
)
task3 = Task(
    description="Aggregate the results of the other agents",
    expected_output="The results of the other agents",
    agent=agent3,
)

crew = Crew(
    agents=[agent, agent2, agent3],
    tasks=[task, task2, task3],
    verbose=True,
)

result = crew.kickoff(inputs={"task": "Generate a random name"})
print(result)
