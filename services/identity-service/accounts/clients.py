

import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def create_customer_in_shop(user):
    shop_service_url = getattr(settings, 'SHOP_SERVICE_URL', 'http://localhost:8001')
    url = f"{shop_service_url}/api/customers/"

    payload = {
        'user_id':user.id,
        'email':user.email,
        'username':user.username
    }

    headers = {
        'Content-Type':'application/json'
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=(3,10)
        )
        response.raise_for_status()

        logger.info(
            "Customer created successfully in shop-service via HTTP",
            extra = {
                'user_id' : user.id,
                'email' : user.email,
                'service':'shop-service',
                'endpoint':url,
                'status_code':response.status_code
            }
        )

        return response.json()

    except requests.exceptions.Timeout:
        logger.error(
            "Timeout while creating customer in shop-service",
            extra = {
                'user_id': user.id,
                'email': user.email,
                'service': 'shop-service',
                'endpoint': url,
                'error_type': 'Timeout',
            }
        )
        return None

    except requests.exceptions.ConnectionError:
        logger.error(
            "Connection error while creating customer in shop-service",
            extra={
                'user_id': user.id,
                'email': user.email,
                'service': 'shop-service',
                'endpoint': url,
                'error_type': 'ConnectionError',
            }
        )
        return None

    except requests.exceptions.HTTPError as e:
        logger.error(
            "HTTP error while creating customer in shop-service",
            extra={
                'user_id': user.id,
                'email': user.email,
                'service': 'shop-service',
                'endpoint': url,
                'error_type': 'HTTPError',
                'status_code': e.response.status_code if e.response else None,
            }
        )
        return None

    except Exception as e:
        logger.exception(
            "Unexpected error while creating customer in shop-service",
            extra={
                'user_id': user.id,
                'email': user.email,
                'service': 'shop-service',
                'endpoint': url,
                'error_type': type(e).__name__,
            }
        )
        return None
