import requests


def get_address_by_zip_code(zip_code: str) -> dict:
    """Fetch address data from ViaCEP service.

    Args:
        zip_code: Postal code in format '99999-999' or '99999999'.
    Returns:
        Dict with address data as returned by ViaCEP.
    Raises:
        requests.HTTPError if the remote service responds with error status.
    """
    response = requests.get(f"https://viacep.com.br/ws/{zip_code}/json/")
    response.raise_for_status()
    return response.json()
