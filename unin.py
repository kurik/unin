import json
import workers

# Open the config file
fcfg = open('unin.cfg')
cfg = json.load(fcfg)

# Start modules
ws = workers.Workers(cfg['workers'])

# Run the loop
for w in ws:
		w.process.start()
