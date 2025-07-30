import json
import requests
from colorama import Fore, Style, init

init(autoreset=True)

class Collection:
    def __init__(
        self,
        user_id,
        db_id,
        coll_id,
        metadata,
        base_url: str = "https://sdk.erioon.com",
    ):
        """
        Initialize a Collection instance.

        Args:
            user_id (str): Authenticated user ID.
            db_id   (str): Database ID.
            coll_id (str): Collection ID.
            metadata (dict): Collection metadata.
            base_url (str): Base URL of the Erioon API.
        """
        self.user_id = user_id
        self.db_id = db_id
        self.coll_id = coll_id
        self.metadata = metadata
        self.base_url = base_url.rstrip("/")

    def _print_loading(self) -> None:
        """Print a green loading message to the terminal."""
        print(Fore.CYAN + "Erioon is loading..." + Style.RESET_ALL)

    # ---------- READ ---------- #
    def get_all(self):
        """
        Retrieve all documents from this collection.

        Usage:
            result = collection.get_all()
        """
        self._print_loading()
        url = f"{self.base_url}/{self.user_id}/{self.db_id}/{self.coll_id}/get_all"
        response = requests.get(url)
        try:
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            return {"status": "KO", "error": str(e), "response": response.json() if response.content else {}}

    def get_specific(self, filters: dict | None = None, limit: int = 1000):
        """
        Retrieve documents matching filters.

        Args:
            filters (dict): Field/value pairs for filtering.
            limit (int): Max number of docs to retrieve (max 500,000).

        Usage:
            result = collection.get_specific(filters={"name": "John"}, limit=100)
        """
        if limit > 500_000:
            raise ValueError("Limit of 500,000 exceeded")
        self._print_loading()

        if filters is None:
            filters = {}

        url = f"{self.base_url}/{self.user_id}/{self.db_id}/{self.coll_id}/get_specific"
        params = {**filters, "limit": limit}
        response = requests.get(url, params=params)
        try:
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            return {"status": "KO", "error": str(e), "response": response.json() if response.content else {}}

    # ---------- CREATE ---------- #
    def insert_one(self, document: dict):
        """
        Insert a single document.

        Args:
            document (dict): The document to insert.

        Usage:
            new_doc = {"name": "Alice", "age": 25}
            result = collection.insert_one(new_doc)
        """
        self._print_loading()
        url = f"{self.base_url}/{self.user_id}/{self.db_id}/{self.coll_id}/insert_one"
        response = requests.post(url, json=document, headers={"Content-Type": "application/json"})
        try:
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            return {"status": "KO", "error": str(e), "response": response.json() if response.content else {}}

    def insert_many(self, documents: list):
        """
        Insert multiple documents at once.

        Args:
            documents (list): List of dicts representing documents.

        Usage:
            docs = [{"name": "A"}, {"name": "B"}]
            result = collection.insert_many(docs)
        """
        self._print_loading()
        url = f"{self.base_url}/{self.user_id}/{self.db_id}/{self.coll_id}/insert_many"
        response = requests.post(url, json={"records": documents})
        try:
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            return {"status": "KO", "error": str(e), "response": response.json() if response.content else {}}

    # ---------- DELETE ---------- #
    def delete_one(self, filter_query: dict):
        """
        Delete a single document matching the query.

        Args:
            filter_query (dict): A query to match one document.

        Usage:
            result = collection.delete_one({"name": "John"})
        """
        self._print_loading()
        url = f"{self.base_url}/{self.user_id}/{self.db_id}/{self.coll_id}/delete_one"
        response = requests.delete(url, json=filter_query)
        try:
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            return {"status": "KO", "error": str(e), "response": response.json() if response.content else {}}

    def delete_many(self, filter_query: dict):
        """
        Delete all documents matching the query.

        Args:
            filter_query (dict): A query to match multiple documents.

        Usage:
            result = collection.delete_many({"status": "inactive"})
        """
        self._print_loading()
        url = f"{self.base_url}/{self.user_id}/{self.db_id}/{self.coll_id}/delete_many"
        response = requests.delete(url, json=filter_query)
        try:
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            return {"status": "KO", "error": str(e), "response": response.json() if response.content else {}}

    # ---------- UPDATE ---------- #
    def update_query(self, filter_query: dict, update_query: dict):
        """
        Update documents matching a filter query.

        Args:
            filter_query (dict): Query to find documents.
            update_query (dict): Update operations to apply.

        Usage:
            result = collection.update_query(
                {"age": {"$gt": 30}},
                {"$set": {"status": "senior"}}
            )
        """
        self._print_loading()
        url = f"{self.base_url}/{self.user_id}/{self.db_id}/{self.coll_id}/update_query"
        response = requests.patch(url, json={"filter_query": filter_query, "update_query": update_query})
        try:
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            return {"status": "KO", "error": str(e), "response": response.json() if response.content else {}}

    # ---------- dunder helpers ---------- #
    def __str__(self) -> str:
        """Return a human-readable JSON string of collection metadata."""
        return json.dumps(self.metadata, indent=4)

    def __repr__(self) -> str:
        """Return a developer-friendly representation of the object."""
        return f"<Collection coll_id={self.coll_id}>"
