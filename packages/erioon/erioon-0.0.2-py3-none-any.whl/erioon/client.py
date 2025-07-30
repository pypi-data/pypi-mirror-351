import os
import json
import requests
from erioon.database import Database

class ErioonClient:
    def __init__(self, email, password, base_url="http://127.0.0.1:5000"):
        self.email = email
        self.password = password
        self.base_url = base_url
        self.user_id = None
        self.error = None
        self.token_path = os.path.expanduser(f"~/.erioon_token_{self._safe_filename(email)}")

        try:
            self.user_id = self._load_or_login()
        except Exception as e:
            self.error = str(e)

    def _safe_filename(self, text):
        return "".join(c if c.isalnum() else "_" for c in text)

    def _load_or_login(self):
        # Try to load from local cache
        if os.path.exists(self.token_path):
            with open(self.token_path, "r") as f:
                token_data = json.load(f)
                user_id = token_data.get("user_id")
                if user_id:
                    return user_id  # ✅ Use cached value without API call

        # Fallback: login and cache
        return self._do_login_and_cache()

    def _do_login_and_cache(self):
        user_id = self._login()
        with open(self.token_path, "w") as f:
            json.dump({"user_id": user_id}, f)
        return user_id

    def _login(self):
        url = f"{self.base_url}/login_with_credentials"
        payload = {"email": self.email, "password": self.password}
        headers = {"Content-Type": "application/json"}

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.text.strip()
        else:
            raise Exception("Invalid account")

    def _clear_cached_token(self):
        if os.path.exists(self.token_path):
            os.remove(self.token_path)
        self.user_id = None

    def __getitem__(self, db_id):
        if not self.user_id:
            raise ValueError("Client not authenticated. Cannot access database.")
    
        try:
            return self._get_database_info(db_id)
        except Exception as e:
            err_msg = str(e).lower()
            # Check if error is a database error mentioning the db_id
            if f"database with {db_id.lower()}" in err_msg or "database" in err_msg:
                # Try relogin once
                self._clear_cached_token()
                try:
                    self.user_id = self._do_login_and_cache()
                except Exception:
                    return "Login error"
    
                # Retry fetching database info
                try:
                    return self._get_database_info(db_id)
                except Exception as e2:
                    print(f"❌ Database with _id {db_id} ...")
                    # Optionally you could also return or raise the error here
                    return f"❌ Database with _id {db_id} ..."
            else:
                # Not a DB-related error, just propagate or raise
                raise e
    

    def _get_database_info(self, db_id):
        payload = {"user_id": self.user_id, "db_id": db_id}
        headers = {"Content-Type": "application/json"}

        response = requests.post(f"{self.base_url}/db_info", json=payload, headers=headers)

        if response.status_code == 200:
            db_info = response.json()
            return Database(self.user_id, db_info)
        else:
            # Try parse error json
            try:
                error_json = response.json()
                error_msg = error_json.get("error", response.text)
            except Exception:
                error_msg = response.text
            raise Exception(error_msg)

    def __str__(self):
        return self.user_id if self.user_id else self.error

    def __repr__(self):
        return f"<ErioonClient user_id={self.user_id}>" if self.user_id else f"<ErioonClient error='{self.error}'>"
