import json
import workers
import hubs

# Open the config file
fcfg = open('unin.cfg')
cfg = json.load(fcfg)

# Initialize hubs
hs = hubs.Hubs(cfg['hubs'])

# Initialize workers
ws = workers.Workers(cfg['workers'], hs)

# Start workers
for w in ws:
		w.process.start()
