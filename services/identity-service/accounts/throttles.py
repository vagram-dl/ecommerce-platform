from rest_framework.throttling import AnonRateThrottle

class AuthRateThrottling(AnonRateThrottle):
    rate = '5/m'
    scope = 'auth'