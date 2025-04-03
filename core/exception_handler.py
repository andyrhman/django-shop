from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.transaction import TransactionManagementError
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    # Handle TransactionManagementError with a JSON response
    if isinstance(exc, TransactionManagementError):
        return Response(
            {"message": str(exc)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # Handle Django's ValidationError with a JSON response
    if isinstance(exc, DjangoValidationError):
        # Extract error messages; they may be a list or a dict
        messages = exc.message_dict if hasattr(exc, 'message_dict') else exc.messages
        return Response(
            {"message": messages},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Let DRF's default exception handler process the error first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Replace 'detail' with 'message' in the response data, if present
        if 'detail' in response.data:
            response.data['message'] = response.data.pop('detail')
    
        # Adjust status code: change 403 to 401, if needed
        if response.status_code == 403:
            response.status_code = 401

    return response
