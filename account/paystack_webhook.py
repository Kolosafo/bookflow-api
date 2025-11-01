from rest_framework.decorators import api_view
from ipware import get_client_ip
from .helpers import check_ip_address
from rest_framework.response import Response
from rest_framework import status
from .models import PaystackResponse
import json

@api_view(['POST'])
def payment_webook(request):
    data = request.data
 
    client_ip, is_routable = get_client_ip(request)
    try:
        if client_ip and is_routable:
            check_from_paystack = check_ip_address(client_ip)
            if  check_from_paystack == False :
                # # print("not paystack")
                return Response({
                    "data": "",
                    "errors": "",
                    "message": "",
                    "status": status.HTTP_400_BAD_REQUEST,
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                PaystackResponse.objects.create(data=data)
                return Response({
                    "data": "",
                    "errors": "",
                    "message": "",
                    "status": status.HTTP_200_OK,
                    }, status=status.HTTP_200_OK)     
          

        else:
            return Response({
                    "data": "",
                    "errors": "",
                    "message": "",
                    "status": status.HTTP_400_BAD_REQUEST,
                    }, status=status.HTTP_400_BAD_REQUEST)        
    
    except Exception as E:
        return Response({
                "data": "",
                "errors": "",
                "message": "e",
                "status": status.HTTP_400_BAD_REQUEST,
                }, status=status.HTTP_400_BAD_REQUEST)
