#!/usr/bin/env python
# Name: JAST - Just Another Screenshot Tool
# Description: JAST is a tool to capture web server screenshots
#   and server information using headless Firefox/Selenium.
# Version: 0.3.1
# Author: Mike Lisi (mike@mikehacksthings.com)

"""
JAST

Usage:
  jast.py [options] (-u URL | -f FILE) -o DIR
  jast.py (-h | --help)
  jast.py (-v | --version)

Arguments:
  -u	Single URL to screenshot.
  -f	File containing hosts to screenshot.
  -o	Output directory.

Screenshot Options:
  -s --size SIZE  	Screenshot window size [default: 800x600].
  --headers  		Include HTTP Headers in report.
  --follow-redirects  	Follow redirects before taking screenshot.

Options:
  -h --help  		Show this screen.
  -v --version  	Show version.
"""

import os
import sys
import time
from docopt import docopt

from host import Host
from browser import Browser
from report import Report
from alert import ALERT, SUCCESS

def process_hosts(data, args):
	hosts = []
	for item in data:
		u = item.rstrip('\n')
		if 'http' not in u:
			print(ALERT + "No protocol supplied for host: {0}. Use format http(s)://<host> Skipping...".format(u))
			continue
		try:
			image_file = u.split('//')[1]
			for c in [':', '/', '.']:
				image_file = image_file.replace(c, '_')

			output_file = "screenshots/" + image_file + "_" + str(int(time.time())) + ".png"
			host = Host(store_headers=args['--headers'], follow_redirects=args['--follow-redirects'])
			host.set_url(u)
			host.set_ss_filename(output_file)
			hosts.append(host)

		except IndexError:  # URL doesn't begin with a protocol
			print(ALERT + "No protocol supplied for host: {0}. Use format http(s)://<host>. Skipping...".format(u))
			continue

	return hosts


def take_screenshot(h, b, args):
	print(SUCCESS + "Taking screenshot for URL: {0}".format(h.get_url()))
	if host.check_host():
		try:
			b.get_url(h.get_url())
			b.save_image(args['-o'] + "/" + h.get_ss_filename())

		except:
			print(ALERT + "Error taking screenshot for host: {0}. Skipping.".format(h.get_url()))
			host.error = True
	else:
		host.error = True


if __name__ == '__main__':
	args = docopt(__doc__, version='JAST - Just Another Screenshot Tool v0.3.1')

	data = []
	hosts = []

	# Check for output dir and prompt for overwrite if it already exists
	if os.path.exists(args['-o']):
		overwrite = input(ALERT + "Output directory exists (" + args['-o'] + "), overwrite? (Y/n): ") or 'y'

		if 'n' in overwrite.lower():
			print(ALERT + "Directory not being overwritten, exiting.")
			sys.exit(-1)
		elif 'y' not in overwrite.lower():
			print(ALERT + "Unknown response, exiting.")
			sys.exit(-1)

	# Parse host file/host
	print(SUCCESS + "Processing host(s)...")
	if args['-f']:
		if os.path.exists(args['-f']) and os.path.isfile(args['-f']):
			f = open(args['-f'], 'r')
			data = f.readlines()
			f.close()
		else: # File doesn't exist
			print(ALERT + "Host file not found! Exiting.")
			sys.exit(-1)

	elif args['-u']:
		data = [args['-u']]

	hosts = process_hosts(data, args)

	if len(hosts) == 0:
		print(ALERT + "No hosts processed, exiting...")
		sys.exit(-1)

	report = Report(args)
	report.create_report_dir()

	browser = Browser(size=args['--size'])
	for host in hosts:
		take_screenshot(host, browser, args)
	browser.close()

	report.start()
	for host in hosts:
		report.write_host(host)
	report.finish()

	print(SUCCESS + "Complete.")
	print(SUCCESS + "Report written to {0}/report.html".format(args['-o']))
