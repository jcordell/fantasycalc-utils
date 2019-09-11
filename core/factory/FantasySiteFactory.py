from services.fantasysites.MFLService import MFLService
from services.fantasysites.ESPNService import ESPNService
from services.fantasysites.FleaflickerService import FleaflickerService

apis = {
    'mfl': MFLService,
    'espn': ESPNService,
    'fleaflicker': FleaflickerService
}


class FantasySiteFactory:
    def get_site_api(self, api_name, year):
        return apis[api_name](year)
