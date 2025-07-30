import json
from requests import get, post
from .types.Invoice import Invoice

class CryptoBot():
    def __init__(self, api_key: str, isTestnet = False):
        """
        CryptoBot is class for using the library
        Params:
        api_key = using for communicate with the cryptobot api
        isTestnet = (Optional) Using for testing the bot with testnet
        """

        self.headers = {'Content-Type': 'application/json', 'Crypto-Pay-API-Token': api_key}  
        if isTestnet:
            self.url = "https://testnet-pay.crypt.bot/api"
        else:
            self.url = "https://pay.crypt.bot/api"

    def createInvoice(self, 
                           amount: str,
                           asset: str, 
                           fiat = None,
                           accepted_assets = None,
                           descriptoion = None,
                           hidden_message = None,
                           paid_btn_name = None,
                           paid_btn_url = None,
                           payload = None,
                           expires_in = None,
                           allow_comments = True,
                           allow_anonymous = True,
                           currency_type = "crypto"):
        """
        createInvoice - function for creating a payment invoice
        
        Params:
            amount {string} - amount of the invoice, in fload
            asset: {string} - Currency code, (BTC, TON, ETH)
            fiat = {string} - Fiat code, (RUB, EUR, USD)
            accepted_assets {string} - List of cryptocurrency alphabetic codes separated comma. Assets which can be used to pay the invoice. Available only if currency_type is “fiat”. 
            descriptoion {string} - description of invoice
            hidden_message {string} - Text of the message which will be presented to a user after the invoice is paid. Up to 2048 characters.
            paid_btn_name {string} - Label of the button which will be presented to a user after the invoice is paid ( viewItem , openChannel , openBot , callback )
            paid_btn_url {string} - Required if paid_btn_name is specified. URL opened using the button which will be presented to a user after the invoice is paid. You can set any callback link 
            payload {string} - Any data you want to attach to the invoice (for example, user ID, payment ID, ect). Up to 4kb.
            expires_in {int} - You can set a payment time limit for the invoice in seconds. Values between 1-2678400 are accepted
            allow_comments {bool} - allow comments
            allow_anonymous {bool} - allow anonymous pay
            currency_type {string} - crypto or fiat):

        Returns a Invoice type       
        """
        
        data_payload = {
            "currency_type": currency_type,
            "amount": amount,
            "asset": asset,
            "allow_anonymous": allow_anonymous,
            "allow_comments": allow_comments
        }

        if fiat is not None: data_payload.update({"fiat": fiat})
        if accepted_assets is not None: data_payload.update({"accepted_assets": accepted_assets})
        if descriptoion is not None: data_payload.update({"descriptoion": descriptoion})
        if hidden_message is not None: data_payload.update({"hidden_message": hidden_message})
        if paid_btn_name is not None: data_payload.update({"paid_btn_name": paid_btn_name})
        if paid_btn_url is not None: data_payload.update({"paid_btn_url": paid_btn_url})
        if payload is not None: data_payload.update({"payload": payload})
        if expires_in is not None: data_payload.update({"expires_in": expires_in})

        req = post(f"{self.url}/createInvoice", json=data_payload, headers=self.headers)
        jsonobj = json.loads(json.dumps(req.json()))["result"]

        # FIXME: Implement the items loop, because cryptobot can give a items list
        if "items" in jsonobj:
            pass

        comment_res = "not_provided_stuff"
        if "comment" in jsonobj: comment_res = jsonobj['comment']
        hidden_message_res = "not_provided_stuff"
        if "hidden_message" in jsonobj: hidden_message_res = jsonobj['comment']
        payload_res = "not_provided_stuff"
        if "payload" in jsonobj: payload_res = jsonobj['payload']
        

        return Invoice(
            invoice_id=jsonobj['invoice_id'],
            hash=jsonobj['hash'],
            currency_type=jsonobj['currency_type'],
            amount=jsonobj['amount'],
            bot_invoice_url=jsonobj['bot_invoice_url'],
            mini_app_invoice_url=jsonobj['mini_app_invoice_url'],
            web_app_invoice_url=jsonobj['web_app_invoice_url'],
            status=jsonobj['status'],
            created_at=jsonobj['created_at'],
            comment=comment_res,
            hidden_message=hidden_message_res,
            payload=payload_res
        )
    
    def getInvoices(self,
                    asset = None,
                    fiat = None,
                    invoice_ids = None,
                    status = None,
                    offset = None,
                    count = None):
        data_payload = {}
        if fiat is not None: data_payload.update({"fiat": fiat})
        if invoice_ids is not None: data_payload.update({"invoice_ids": invoice_ids})
        if status is not None: data_payload.update({"status": status})
        if asset is not None: data_payload.update({"asset": asset})
        if offset is not None: data_payload.update({"offset": offset})
        if count is not None: data_payload.update({"count": count})

        items = []

        req = get(f"{self.url}/getInvoices", headers=self.headers, json=data_payload)
        for i in req.json()["result"]["items"]:
            comment_res = "not_provided_stuff"
            if "comment" in i: comment_res = i['comment']
            hidden_message_res = "not_provided_stuff"
            if "hidden_message" in i: hidden_message_res = i['comment']
            payload_res = "not_provided_stuff"
            if "payload" in i: payload_res = i['payload']
            items.append(Invoice(
                invoice_id=i['invoice_id'],
                hash=i['hash'],
                currency_type=i['currency_type'],
                amount=i['amount'],
                bot_invoice_url=i['bot_invoice_url'],
                mini_app_invoice_url=i['mini_app_invoice_url'],
                web_app_invoice_url=i['web_app_invoice_url'],
                status=i['status'],
                created_at=i['created_at'],
                comment=comment_res,
                hidden_message=hidden_message_res,
                payload=payload_res
            ))
        return items
    
    
    def checkInvoice(self, invoice: Invoice):
        invoice_id = invoice.invoice_id()
        req = self.getInvoices(invoice_ids=invoice_id)
        if req[0]:
            return req[0].status()
        else:
            return "notfound"
        
        
        



