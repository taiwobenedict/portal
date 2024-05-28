from api_errors.models import ErrorResponses

def ReturnErrorResponse(info, api_name, default_text):
  try:
    get_errors = ErrorResponses.objects.filter(name_of_api__icontains=api_name, error_code__icontains=info)
    return get_errors[0].error_description
  except Exception as e:
    return default_text