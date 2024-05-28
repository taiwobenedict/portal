from other_data_services.imports import *

class GetDetailsTransactions(APIView):
  authentication_classes = (QueryStringBasedTokenAuthentication,)
  permission_classes = (IsAuthenticated,)
  def get(self, request):
    try:
      params = request.query_params
      token = getApiKey(request)
      getUser = get_or_none(Token, key=token)
      if getUser != None:
        user = getUser.user

        transId = params['transId']
        broadband = params['broadband']

        if broadband == 'smile':
          apiParams = SmilesApis.objects.get(is_active=True).res_params
          details = generateDetailsFromBroadBand(SmileTransactions, user=user, transId=transId, res_params=apiParams)
          if details[1] is True:
            return Response({"status":200, "message":"Details retrieved successfully", "details": details[0]})
          else:
            return Response({"status":404, "message":"Details not Available", "details": details[0]})
        elif broadband == 'spectranet':
          apiParams = SpectranetApis.objects.get(is_active=True).res_params
          details = generateDetailsFromBroadBand(SpectranetTransactions, user=user, transId=transId, res_params=apiParams)
          if details[1] is True:
            return Response({"status":200, "message":"Details retrieved successfully", "details": details[0]})
          else:
            return Response({"status":404, "message":"Details not Available", "details": details[0]})
      else:
        return Response({"status":403, "message": "Error", "details":"Not Authorized"})
    except Exception as e:
      raise e
      return Response({"status":403, "message": "Error", "details":"Bad Request"})
