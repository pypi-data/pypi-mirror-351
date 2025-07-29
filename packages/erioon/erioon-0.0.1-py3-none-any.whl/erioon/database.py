import json

class Database:
    def __init__(self, metadata):
        self.metadata = metadata

    def __getitem__(self, collection_id):
        """
        Will return a Collection object (to be implemented in next steps).
        """
        raise NotImplementedError("Collection access not implemented yet.")

    def __str__(self):
        return json.dumps(self.metadata, indent=4)

    def __repr__(self):
        return f"{self.metadata}"
