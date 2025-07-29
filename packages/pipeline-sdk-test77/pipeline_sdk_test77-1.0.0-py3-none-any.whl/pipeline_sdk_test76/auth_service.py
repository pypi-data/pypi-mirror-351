import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from config import Config
 
USERNAME = Config.USERNAME
PASSWORD = Config.PASSWORD
# Kubeflow base URL
BASE_URL = Config.BASE_URL
 
def fetch_login_form(session: requests.Session) -> str:
    """
    Fetches and returns the login form action URL.
    """
    print("Visiting Kubeflow base URL...")
    response = session.get(BASE_URL, allow_redirects=True)
    print(f"Status Code: {response.status_code}")
    print(f"Final URL after redirect: {response.url}")
 
    soup = BeautifulSoup(response.text, 'html.parser')
    form = soup.find('form')
 
    if not form:
        print("Login form not found.")
        print("HTML snippet:")
        print(response.text[:1000])
        return None
 
    form_action = form.get('action')
    if not form_action:
        print("No 'action' found in login form.")
        return None
 
    return urljoin(BASE_URL, form_action)
 
def perform_login(session: requests.Session, login_url: str) -> str:
    """
    Submits the login credentials and returns the auth token (cookie).
    """
    creds = {'login': USERNAME, 'password': PASSWORD}
    print(f"Submitting credentials to: {login_url}")
    login_response = session.post(
        login_url,
        data=creds,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        allow_redirects=True
    )
 
    print(f"Login response code: {login_response.status_code}")
    print(f"Final URL after login: {login_response.url}")
 
    return session.cookies.get("authservice_session")
 
def get_auth_token() -> str:
    """
    Fetches authentication token for Kubeflow (Dex login flow).
    """
    session = requests.Session()
    login_url = fetch_login_form(session)
 
    if not login_url:
        print("Failed to extract login URL.")
        return None
 
    auth_token = perform_login(session, login_url)
    if not auth_token:
        print("authservice_session cookie not found.")
        return None
 
    print(f"Auth Token: {auth_token}")
    return auth_token
 
if __name__ == "__main__":
    get_auth_token()