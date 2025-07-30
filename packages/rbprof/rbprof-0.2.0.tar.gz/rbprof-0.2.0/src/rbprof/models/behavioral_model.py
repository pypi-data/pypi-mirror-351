class BehaviorModel:
    def __init__(self):
        self.normal_actions = {"open", "read"}

    def is_anomalous(self, entry: Dict) -> bool:
        """
        Determines if an entry is anomalous.
        """
        action = entry.get("action")
        return action not in self.normal_actions