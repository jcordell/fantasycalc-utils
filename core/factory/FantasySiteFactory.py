from services.fantasysites.MFLService import MFLService
from services.fantasysites.ESPNService import ESPNService

apis = {
    'mfl': MFLService,
    'espn': ESPNService
}


class FantasySiteFactory:
    def get_site_api(self, api_name, year):
        return apis[api_name](year)
