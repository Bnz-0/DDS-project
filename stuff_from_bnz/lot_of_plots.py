#!/usr/bin/env python3

import subprocess as sub

args = {
	'N': None,
	'K': 2,
	'NODE_LIFETIME': None,
	'NODE_UPTIME': None,
	'NODE_DOWNTIME': None,
	'DATA_SIZE': None,
	'UPLOAD_SPEED': None,
	'DOWNLOAD_SPEED': None,
	'SERVER_LIFETIME': None,
	'SERVER_UPTIME': None,
	'SERVER_DOWNTIME': None,
	'MAXTMULTI_BLOCK_SERVER': None,
}

def flat(d):
	flat_args = []
	for k,v in d.items():
		if v is not None:
			flat_args += [k, str(v)]
	return flat_args

def parse_event(line):
	t, event, *result = line.split(' ')
	return float(t), event, result[0] == "[DONE]" if len(result) > 0 else None

def run():
    p = sub.run(['./backup_redacted_multi.py'] + flat(args), check=True, capture_output=True)
    return [parse_event(l.decode('utf-8').strip()) for l in p.stdout.split(b'\n') if len(l) > 0]


# TODO: a lot of plots

print(run())
