class ObjectDoesNotExist(Exception):
    status = 404

    def __init__(self, label: str) -> None:
        self.label = label
        super().__init__(f"{label} not found.")
