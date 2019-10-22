class InvalidCredentials(Exception):
    status = 401

    def __init__(self) -> None:
        super().__init__("Invalid credentials.")


class ObjectDoesNotExist(Exception):
    status = 404

    def __init__(self, label: str) -> None:
        super().__init__(f"{label} not found.")
        self.label = label
