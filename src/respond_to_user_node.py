class RespondToUserNode:
    def __init__(self, state):
        self.state = state

    def send_response(self, formatted_hint):
        # Logic to send the response to the user
        print(formatted_hint)
        return formatted_hint
