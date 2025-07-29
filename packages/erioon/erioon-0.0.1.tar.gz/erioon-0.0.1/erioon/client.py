import requests
from erioon.database import Database

class ErioonClient:
    """
    Represents an authenticated Erioon client session.

    Handles user login via email and password, and stores either the user's ID 
    on success or an error message on failure.

    Usage:
    >>> client = ErioonClient("<EMAIL>:<PASSWORD>")
    """

    def __init__(self, email, password, base_url="https://sdk.erioon.com"):
        """
        Initializes the client and attempts login.

        Args:
            email (str): User email address.
            password (str): User password.
            base_url (str): The base URL of the Erioon API.
        """
        self.email = email
        self.password = password
        self.base_url = base_url
        self.user_id = None
        self.error = None 

        try:
            self.user_id = self.login()
        except Exception as e:
            self.error = str(e)

    def login(self):
        """
        Sends a login request to the Erioon API.

        Returns:
            str: User ID on successful login.

        Raises:
            Exception: If the login fails, with the error message from the server.
        """
        url = f"{self.base_url}/login_with_credentials"
        payload = {"email": self.email, "password": self.password}
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            return response.text.strip()
        else:
            raise Exception(response.text.strip())

    def __str__(self):
        """
        Called when print() or str() is used on the object.

        Returns:
            str: User ID if authenticated, or error message if not.
        """
        return self.user_id if self.user_id else self.error

    def __repr__(self):
        """
        Called in developer tools or when inspecting the object.

        Returns:
            str: Formatted string showing either user ID or error.
        """
        if self.user_id:
            return f"<ErioonClient user_id={self.user_id}>"
        else:
            return f"<ErioonClient error='{self.error}'>"

    def __getitem__(self, db_id):
        """
        Get a Database object by its ID.

        Calls the API to retrieve DB metadata and initializes a Database instance.
        """
        if not self.user_id:
            raise ValueError("Client not authenticated. Cannot access database.")
        
        payload = {"user_id": self.user_id, "db_id": db_id}
        headers = {"Content-Type": "application/json"}

        response = requests.post(f"{self.base_url}/db_info", json=payload, headers=headers)


        if response.status_code != 200:
            db_error = response.json()
            return db_error["error"]

        db_info = response.json()
        return Database(db_info)

    def __str__(self):
        return self.user_id if self.user_id else self.error

    def __repr__(self):
        if self.user_id:
            return f"<ErioonClient user_id={self.user_id}>"
        else:
            return f"<ErioonClient error='{self.error}'>"