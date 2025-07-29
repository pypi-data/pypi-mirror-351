# -*- coding: utf-8 -*-
import logging

from moova.connector import Connector, ConnectorException
from moova.settings import api_settings

logger = logging.getLogger(__name__)


class MoovaHandler:
    """
        Handler to send shipping payload to Moova
    """
    def __init__(self, base_url=api_settings.MOOVA['BASE_URL'],
                 secret=api_settings.MOOVA['SECRET'],
                 key=api_settings.MOOVA['KEY'],
                 type=api_settings.MOOVA['TYPE'],
                 flow=api_settings.MOOVA['FLOW'],
                 verify=True, **kwargs):

        self.base_url = kwargs.pop('base_url', base_url)
        self.secret = kwargs.pop('secret', secret)
        self.key = kwargs.pop('key', key)
        self.verify = kwargs.pop('verify', verify)
        self.type = kwargs.pop('type', type)
        self.flow = kwargs.pop('flow', flow)
        self.connector = Connector(self._headers(), verify_ssl=self.verify)

    def _headers(self):
        """
            Here define the headers for all connections with Moova.
        """
        return {
            'Authorization': self.secret,
            'Content-Type': 'application/json'
        }

    def get_shipping_label(self, tracking_number):
        """
            This method helps us to obtain the url of the label for
            our shipping created.
        """
        url = f'{self.base_url}shippings/{tracking_number}/label/?appId={self.key}'

        try:
            response = self.connector.get(url)
            return response['label']
        except ConnectorException as error:
            logger.error(error)
            raise ConnectorException(error.message, error.description, error.code) from error

    def get_default_payload(self, instance):
        """
            This method generates by default all the necessary data with
            an appropriate structure for Moova courier.
        """
        from_data = {
            'address': api_settings.SENDER['ADDRESS'],
            'country': api_settings.SENDER['COUNTRY'],
            'instructions': api_settings.SENDER['INSTRUCTIONS'],
            'contact': {
                'firstName': api_settings.SENDER['FIRST_NAME'],
                'lastName': api_settings.SENDER['LAST_NAME'],
                'email': api_settings.SENDER['EMAIL'],
                'phone': api_settings.SENDER['PHONE']
            }
        }

        payload = {
            'currency': api_settings.MOOVA['CURRENCY'],
            'type': 'next_day' if getattr(instance.extra_args, 'type', self.type) == 'same_day' else getattr(instance.extra_args, 'type', self.type),
            'flow': self.flow,
            'from': from_data,
            'to': {
                'address': f'{instance.address.street} {instance.address.number}, {instance.commune.name}, {instance.region.name}, Chile',
                'country': api_settings.SENDER['COUNTRY'],
                'instructions': instance.address.full_address,
                'contact': {
                    'firstName': instance.customer.first_name,
                    'lastName': instance.customer.last_name,
                    'email': instance.customer.email,
                    'phone': instance.customer.phone
                },
                'message': ''
            },
            'internalCode': instance.reference,
            'extra': {},
            'items': [],
            'conf': {
                'assurance': None,
            }
        }

        if hasattr(instance, 'items'):
            payload['items'] = [
                {
                'description': item.name,
                'price': float(item.price),
                'weight': None,
                'width': None,
                'length': None,
                'height': None,
                'quantity': item.quantity,
                } for item in instance.items
            ]

        logger.debug(payload)
        return payload

    def create_shipping(self, data):
        """
            This method generate a Moova shipping.
            If the get_default_payload method returns data, send it here,
            otherwise, generate your own payload.

            Additionally data was added to the response:
                tracking_number -> number to track the shipment.
                label -> url for view label.
        """
        url = f'{self.base_url}shippings?appId={self.key}'
        logger.debug(data)

        try:
            response = self.connector.post(url, data)
            tracking_number = response.get('id')

            logger.debug(tracking_number, response)
            body = {**response, 'tracking_number': tracking_number}

        except ConnectorException as error:
            logger.error(error)
            raise ConnectorException(error.message, error.description, error.code) from error

        try:
            label = self.get_shipping_label(body.get('tracking_number'))
            return {**body, 'label': label}
        except ConnectorException as error:
            return {**body, 'label': error.description}

    def get_tracking(self, tracking_number):
        """
            This method obtain a detail a shipping of Moova.
        """
        url = f'{self.base_url}shippings/{tracking_number}?appId={self.key}'

        try:
            response = self.connector.get(url)
            logger.debug(response)
            return response
        except ConnectorException as error:
            logger.error(error)
            raise ConnectorException(error.message, error.description, error.code) from error

    def get_events(self, raw_data):
        """
            This method obtain array events.
            structure:
            {
                'tracking_number': '8decd780-aff3-11ee-a811-a92d496b639c',
                'status': 'DELIVERED',
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
                'status': 'DELIVERED',
                'details': [{
                    'scheduled': '2023-01-10 19:20:04'
                    'range': '300',
                }]
                'date': '2023-01-10 19:20:04',
            }

            status : ['DRAFT', 'READY', 'CONFIRMED', 'ATPICKUPPOINT',
                       'PICKEDUP', 'INTRANSIT', 'DELIVERED', 'CANCELED', 'INCIDENCE',
                       'TOBERETURNED', 'RETURNED']
            response: ('DELIVERED', True)
        """

        status = raw_data.get('status')
        is_delivered = False

        if status == 'DELIVERED':
            is_delivered = True

        return status, is_delivered
