from agent import get_thud_agent

class FindHintNode:
    def __init__(self, state):
        self.state = state

    def retrieve_hint(self, user_input):
        # Use the existing thud agent to get hints
        agent = get_thud_agent()
        hint = agent.run(user_input)
        return hint
