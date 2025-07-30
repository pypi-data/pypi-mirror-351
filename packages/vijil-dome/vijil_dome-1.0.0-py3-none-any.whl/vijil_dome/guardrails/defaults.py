from vijil_dome.detectors import (
    PI_MBERT,
    PRIVACY_PRESIDIO,
    MODERATION_DEBERTA,
    MODERATION_FLASHTXT_BANLIST,
)


class DefaultGuardrailConfig:
    def __init__(self):
        self.security_default = {
            "security_default": {
                "type": "security",
                "exit-early": True,
                "methods": [PI_MBERT],
            }
        }
        self.moderation_default = {
            "moderation_default": {
                "type": "moderation",
                "exit-early": True,
                "methods": [MODERATION_DEBERTA, MODERATION_FLASHTXT_BANLIST],
            }
        }

        self.privacy_default = {
            "privacy_default": {"type": "privacy", "methods": [PRIVACY_PRESIDIO]}
        }

        self.default_guardrail_config = {
            "input-guards": [self.security_default, self.moderation_default],
            "output-guards": [self.moderation_default, self.privacy_default],
        }


def get_default_guardrail_config():
    return DefaultGuardrailConfig().default_guardrail_config
