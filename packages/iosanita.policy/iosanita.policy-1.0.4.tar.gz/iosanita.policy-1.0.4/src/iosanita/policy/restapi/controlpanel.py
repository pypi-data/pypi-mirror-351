from iosanita.policy.interfaces import IIosanitaPolicyLayer
from iosanita.policy.interfaces import IIoSanitaSettings
from iosanita.policy.interfaces import IIoSanitaSettingsControlpanel
from plone.restapi.controlpanels import RegistryConfigletPanel
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@adapter(Interface, IIosanitaPolicyLayer)
@implementer(IIoSanitaSettingsControlpanel)
class IoSanitaSettingsControlpanel(RegistryConfigletPanel):
    schema = IIoSanitaSettings
    configlet_id = "IoSanitaSettings"
    configlet_category_id = "Products"
    schema_prefix = None
