class LoopsCounter:
    """Class for checking whether on current iteration it is allowed to run function or not"""

    def __init__(self):
        self.required_loops_number = 0
        self.current_loops_number = 0

    def set_required_loops_number_by_seconds(self, loop_duration: int, required_seconds: int):
        """Calculates required loops number and sets it"""

        required_loops_number = required_seconds // loop_duration
        self.required_loops_number = required_loops_number

    def count(self):
        """Increase current loops number"""

        self.current_loops_number += 1

    def check(self) -> bool:
        """Check if current loops number >= required loops number"""

        if self.current_loops_number >= self.required_loops_number:
            self.current_loops_number = 0
            return True
        return False
