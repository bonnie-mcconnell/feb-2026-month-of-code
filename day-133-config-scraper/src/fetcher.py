import requests


DEFAULT_TIMEOUT = 5.0
USER_AGENT = "config-scraper/1.0"


def fetch_url(url: str, timeout: float = DEFAULT_TIMEOUT) -> dict:
    headers = {
        "User-Agent": USER_AGENT
    }

    try:
        response = requests.get(url, headers=headers, timeout=timeout)
    except requests.exceptions.Timeout:
        return {
            "ok": False,
            "status_code": None,
            "content": None,
            "error": "timeout"
        }
    except requests.exceptions.ConnectionError:
        return {
            "ok": False,
            "status_code": None,
            "content": None,
            "error": "connection_error"
        }
    except requests.RequestException as e:
        return {
            "ok": False,
            "status_code": None,
            "content": None,
            "error": f"request_exception: {str(e)}"
        }

    if response.status_code != 200:
        return {
            "ok": False,
            "status_code": response.status_code,
            "content": None,
            "error": f"http_{response.status_code}"
        }

    return {
        "ok": True,
        "status_code": response.status_code,
        "content": response.text,
        "error": None
    }
