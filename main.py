from core.updaters.FantasySiteUpdater import FantasySiteUpdater
import config

# iterates over all specified fantasy sites and updates settings


def update_settings(fantasy_sites, year):
    for site in fantasy_sites:
        site = FantasySiteUpdater(site, year)
        site.update_settings()

# iterates over all specified fantasy sites and updates trades


def update_trades(fantasy_sites, year):
    for site in fantasy_sites:
        site = FantasySiteUpdater(site, year)
        site.update_trades()


'''
Use configurations from config file to control updaters
'''
if __name__ == "__main__":
    # can have this set in command line arg
    run_config = config.LocalHostConfig

    if run_config.UPDATE_SETTINGS:
        update_settings(run_config.SITES, run_config.YEAR)

    if run_config.UPDATE_TRADES:
        update_trades(run_config.SITES, run_config.YEAR)
