class CRMWrapper:
    def __init__(self, sdk):
        self._sdk = sdk

    @property
    def deals(self):
        return self._sdk.crm_deals

class SDKWrapper:
    def __init__(self, sdk):
        self._sdk = sdk
        self.crm = CRMWrapper(sdk)

    def __getattr__(self, name):
        return getattr(self._sdk, name)