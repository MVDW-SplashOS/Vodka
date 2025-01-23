def createAPIResponse(response_code, data = None, reason = None):
    response = {
        "response_code" : response_code
    }

    if data is not None:
        response.update({"data" : data})

    if reason is not None:
        response.update({"reason" : reason})

    return response
