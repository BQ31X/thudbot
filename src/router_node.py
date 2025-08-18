class RouterNode:
    def __init__(self, state):
        self.state = state

    def is_hint_request(self, user_input):
        # Simple logic to determine if the input is a hint request
        return 'hint' in user_input.lower()

    def is_repeat(self, user_input):
        # Check if the current input is a repeat of the last question
        return user_input == self.state.get('last_question_id')

    def route(self, user_input):
        if not self.is_hint_request(user_input):
            return 'respond_directly'
        if self.is_repeat(user_input):
            self.state['hint_level'] += 1
            return 'hint_escalation'
        else:
            self.state['last_question_id'] = user_input
            self.state['hint_level'] = 1
            return 'new_query'
