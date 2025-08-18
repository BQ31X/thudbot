class FormatOutputNode:
    def __init__(self, state):
        self.state = state

    def format_hint(self, hint):
        # Simple formatting logic for the final output
        return f"Here's your hint: {hint}"
