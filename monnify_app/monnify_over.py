from monnify.monnify import Monnify
import json, requests

class MonnifyV2(Monnify):

    """Create Reserve Account v2"""
    def createReserveAccountV3(self, **kwargs):
        rHeaders = {'Content-Type':"application/json", 'Authorization':"Bearer {0}".format(self.generateToken())}
        reserveAccUrl = "https://api.monnify.com/api/v2/bank-transfer/reserved-accounts"

        _data = {}
        if kwargs.get("bvn_kyc"):
          _data["bvn_kyc"] = kwargs["bvn_kyc"]
        if kwargs.get("nin_kyc"):
          _data["nin_kyc"] = kwargs["nin_kyc"]

        data = {
            "accountReference": kwargs['accountReference'],
            "accountName": kwargs['accountName'],
            "currencyCode": kwargs['currencyCode'],
            "contractCode": kwargs['contractCode'],
            "customerEmail": kwargs['customerEmail'],
            "customerName": kwargs['customerName'],
            "getAllAvailableBanks": kwargs['getAllAvailableBanks'],
            **_data
        }

        createReserveAccount = requests.post(reserveAccUrl, data=json.dumps(data), headers=rHeaders)
        reserverR = json.loads(createReserveAccount.content)
        #print("==>", reserverR)
        return reserverR
    

    """update bvn nin v2"""
    def updateBvnNin(self, **kwargs):
        rHeaders = {'Content-Type':"application/json", 'Authorization':"Bearer {0}".format(self.generateToken())}
        reserveAccUrl = f"https://api.monnify.com/api/v1/bank-transfer/reserved-accounts/{kwargs['accountReference']}/kyc-info"

        _data = {}
        if kwargs.get("bvn_kyc"):
          _data["bvn_kyc"] = kwargs["bvn_kyc"]
        if kwargs.get("nin_kyc"):
          _data["nin_kyc"] = kwargs["nin_kyc"]

        data = {
            **_data
        }

        createReserveAccount = requests.put(reserveAccUrl, data=json.dumps(data), headers=rHeaders)
        reserverR = json.loads(createReserveAccount.content)
        #print("==>", reserverR)
        return reserverR