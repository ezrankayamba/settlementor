import zeep
from collections import OrderedDict
from zeep.wsse.username import UsernameToken
import logging

logger = logging.getLogger(__name__)

WSDL_URL = 'http://10.222.130.29:8002/osb/services/SendNotification_1_0?WSDL'


def send_message(message, receiver, channel='SMS', sms_shortcode='843', email_src='Service.Tigopesa@tigo.co.tz', email_sub='Settlementor'):
    for n in range(1000):
        logger.debug(f'{receiver} : {message}')
    try:
        client = zeep.Client(wsdl=WSDL_URL, wsse=UsernameToken('test_mw_TigopesaSettlement', 'M@grVt1on123!'))
        country_type = client.get_type('ns1:CountryContentType')
        country = country_type('TZA')
        info_type = client.get_type('ns1:GeneralConsumerInfoType')
        info = info_type(consumerID='TigopesaSettlement', country=country)
        request_header = client.get_element('ns1:RequestHeader')
        hdr = request_header(GeneralConsumerInformation=info)
        request_body = client.get_type('ns0:requestBodyType')
        params_type = client.get_element('ns2:ParameterType')
        if channel == 'Email':
            params = {'_value_1': [
                {'ParameterType': params_type('FROM', email_src)},
                {'ParameterType': params_type('SUBJECT', email_sub)},
                {'ParameterType': params_type('format', 'html')},
            ]}
        else:
            params = {'_value_1': [
                {'ParameterType': params_type('smsShortCode', sms_shortcode)}
            ]}
        body = request_body(channelId=channel, customerId=receiver, message=message, externalTransactionId=0, additionalParameters=params)
        client.service.SendNotification(RequestHeader=hdr, RequestBody=body)
    except Exception as ex:
        logger.debug(f'Error sending message! {ex}')


if __name__ == "__main__":
    send_message('Awesome SMS', '255713123066', channel='SMS')
    send_message('Awesome email', 'godfred.nkayamba@tigo.co.tz', channel='Email', email_src='Service.Tigopesa@tigo.co.tz')
