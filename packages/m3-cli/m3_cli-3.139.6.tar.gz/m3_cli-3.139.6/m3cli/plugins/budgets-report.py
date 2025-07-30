"""
The custom logic for the command m3 budgets-report
This logic is created to convert parameters from the Human readable format to
appropriate for M3 SDK API request.
"""
import json

from m3cli.services.request_service import BaseRequest


def create_custom_request(request: BaseRequest) -> BaseRequest:
    params = request.parameters
    params['tenantNames'] = [params.pop('tenantGroup')]
    if 'region' in params:
        params['regionNames'] = [params.pop('region')]
    if params.get('cloud') and params.get('regionNames'):
        raise ValueError("Cannot specify both 'cloud' and 'region'")
    return request


def create_custom_response(request, response):
    try:
        response = json.loads(response)
    except json.decoder.JSONDecodeError:
        return response
    return response
