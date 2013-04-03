import json
import modules

# Open the config file
fcfg = open('unin.cfg')
cfg = json.load(fcfg)

# Start modules
ms = modules.Modules(cfg['modules'])
