from iosanita.policy import _
from iosanita.policy.interfaces import IIoSanitaSettings
from plone.app.registry.browser import controlpanel


class IoSanitaSettingsForm(controlpanel.RegistryEditForm):
    schema = IIoSanitaSettings
    label = _("iosanita_settings_label", default="Io-Sanità Settings")


class IoSanitaControlPanel(controlpanel.ControlPanelFormWrapper):
    form = IoSanitaSettingsForm
