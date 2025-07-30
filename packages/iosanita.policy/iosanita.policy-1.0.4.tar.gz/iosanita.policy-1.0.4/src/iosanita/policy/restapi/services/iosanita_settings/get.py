# -*- coding: utf-8 -*-
from iosanita.policy.interfaces import IIoSanitaSettings
from plone import api
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

import json


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class IoSanitaSettings(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        """
        Bypass expand variable: it's always expanded because we always need this data.
        """
        result = {
            "iosanita-settings": {
                "@id": f"{self.context.absolute_url()}/@iosanita-settings-data"
            }
        }

        result["iosanita-settings"]["contatti_testata"] = self.get_field_from_registry(
            field_name="contatti_testata"
        )

        return result

    def get_field_from_registry(self, field_name):
        try:
            value = (
                api.portal.get_registry_record(field_name, interface=IIoSanitaSettings)
                or ""  # noqa
            )
        except KeyError:
            return None
        if value:
            value = json.loads(value)
        else:
            value = None
        return value


class IoSanitaSettingsGet(Service):
    def reply(self):
        data = IoSanitaSettings(self.context, self.request)
        return data()["iosanita-settings"]
