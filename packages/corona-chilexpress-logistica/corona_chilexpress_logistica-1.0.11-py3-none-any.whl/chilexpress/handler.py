# -*- coding: utf-8 -*-
import logging

from chilexpress.connector import Connector, ConnectorException
from chilexpress.settings import api_settings

logger = logging.getLogger(__name__)


class ChilexpressHandler:
    """
        Handler to send shipping payload to Chilexpress
    """
    def __init__(self, base_url=api_settings.CHILEXPRESS['BASE_URL'],
                 version=api_settings.CHILEXPRESS['VERSION'],
                 card_number=api_settings.CHILEXPRESS['CARD_NUMBER'],
                 key=api_settings.CHILEXPRESS['KEY'],
                 marketplace_rut=api_settings.SENDER['MARKET_PLACE_RUT'],
                 seller_rut=api_settings.SENDER['SELLER_RUT'],
                 verify=True, **kwargs):

        self.base_url = kwargs.pop('base_url', base_url)
        self.version = kwargs.pop('version', version)
        self.card_number = kwargs.pop('card_number', card_number)
        self.marketplace_rut = kwargs.pop('marketplace_rut', marketplace_rut)
        self.seller_rut = kwargs.pop('seller_rut', seller_rut)
        self.key = kwargs.pop('key', key)
        self.verify = kwargs.pop('verify', verify)
        self.connector = Connector(self._headers(), verify_ssl=self.verify)

    def _headers(self):
        """
            Here define the headers for all connections with Moova.
        """
        return {
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache',
            'Ocp-Apim-Subscription-Key': self.key
        }

    def get_shipping_label(self, tracking_number):
        raise NotImplementedError(
            'get_shipping_label is not a method implemented for ChilexpressHandler')

    def get_default_payload(self, instance):
        """
            This method generates by default all the necessary data with
            an appropriate structure for Chilexpress courier.

            Parameters for packages:
                serviceDeliveryCode (int): Código del servicio disponible;
                    2 = PRIORITARIO (PREX), 3 = EXPRESS (CHEX),
                    4 = EXTENDIDO (XTEN), 5 = EXTREMOS (XTRE)
                productCode (int): Código del tipo de roducto a enviar;
                    1 = Documento, 3 = Encomienda
        """
        try:
            payload = {
                'header': {
                    'certificateNumber': 0,
                    'customerCardNumber': self.card_number,
                    'countyOfOriginCoverageCode': api_settings.SENDER['COUNTY_CODE'],
                    'labelType': api_settings.CHILEXPRESS['LABEL_TYPE'],
                    'marketplaceRut': self.marketplace_rut,
                    'sellerRut': self.seller_rut,
                },
                'details': [{
                    'addresses': [
                        {
                            'addressId': 0,
                            'countyCoverageCode': api_settings.SENDER['COUNTY_CODE'],
                            'streetName': api_settings.SENDER['STREET'],
                            'streetNumber': api_settings.SENDER['STREET_NUMBER'],
                            'supplement': api_settings.SENDER['SUPPLEMENT'],
                            'addressType': api_settings.SENDER['ADDRESS_TYPE'],
                            'observation': 'Warehouse address'
                        },
                        {
                            'countyCoverageCode': instance.commune.code,
                            'streetName': instance.address.street,
                            'streetNumber': instance.address.number,
                            'supplement': instance.address.unit or '',
                            'addressType': 'DEST',
                            'observation': 'Customer address'
                        },
                    ],
                    'contacts': [
                        {
                            'name': api_settings.SENDER['FULL_NAME'],
                            'phoneNumber': api_settings.SENDER['PHONE'],
                            'mail': api_settings.SENDER['EMAIL'],
                            'contactType': 'R'
                        },
                        {
                            'name': instance.customer.full_name,
                            'phoneNumber': instance.customer.phone,
                            'mail': instance.customer.email,
                            'contactType': 'D'
                        }
                    ],
                    'packages': [
                        {
                            'weight': 1,
                            'height': 1,
                            'width': 1,
                            'length': 1,
                            'serviceDeliveryCode': "8" if instance.extra_args.type == "next_day" else api_settings.CHILEXPRESS['SERVICE_DELIVERY_CODE'],
                            'productCode': api_settings.CHILEXPRESS['PRODUCT_CODE'],
                            'deliveryReference': instance.reference,
                            'groupReference': f'GRUPO {instance.reference}',
                            'declaredValue': '1',
                            'declaredContent': '5'
                        }
                    ]
                }]
            }

            logger.debug(payload)
            return payload
        except Exception as error:
            logger.error(error)
            return False

    def create_shipping(self, data):
        """
            This method generate a Chilexpress shipping.
            If the get_default_payload method returns data, send it here,
            otherwise, generate your own payload.

            It allows to generate individual or multiple shipments that will remain
            associated with a tracking number or Transport Order, along with
            deliver the label that must be added to your products.

            Returns:
                data (dict): Generated order data
                statusCode (int): Result code
                statusDescription (str): Description of the result
                milliseconds (int): Server error time
                errors (list): Description of the error presented, if applicable.
        """

        logger.debug(data)
        try:
            url = f'{self.base_url}transport-orders/api/{self.version}/transport-orders'
            response = self.connector.post(url, data)
            logger.debug(response)
            if response.get('statusCode', None) != 0:
                logger.error(response)
                return False

            tracking_number = response.get('data').get('detail')[0].get('transportOrderNumber')
            body = {**response, 'tracking_number': int(tracking_number)}
            return body
        except ConnectorException as error:
            logger.error(error)
            return False

    def get_events(self, raw_data):
        """
            This method obtain array events.
            structure:
            {
                'tracking_number': '8decd780-aff3-11ee-a811-a92d496b639c',
                'status': 'PIEZA ENTREGADA A DESTINATARIO',
                'details': [{
                    'scheduled': '2023-01-10 19:20:04'
                    'range': '300',
                }]
                'date': '2023-01-10 19:20:04',
            }
            return [{
                'scheduled': '2023-01-10 19:20:04'
                'range': '300',
            }]
        """
        return raw_data.get('details')

    def get_status(self, raw_data):
        """
            This method returns the status of the order and "is_delivered".
            structure:
            {
                'tracking_number': '8decd780-aff3-11ee-a811-a92d496b639c',
                'status': 'PIEZA ENTREGADA A DESTINATARIO',
                'details': [{
                    'scheduled': '2023-01-10 19:20:04'
                    'range': '300',
                }]
                'date': '2023-01-10 19:20:04',
            }

            status : ['PIEZA ENTREGADA A DESTINATARIO', ...]
            response: ('PIEZA ENTREGADA A DESTINATARIO', True)
        """

        status = raw_data.get('status')
        is_delivered = False

        if status == 'PIEZA ENTREGADA A DESTINATARIO':
            is_delivered = True

        return status, is_delivered
