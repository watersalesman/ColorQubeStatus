#!/usr/bin/env python3

import re
import requests
import shlex
import sys
from bs4 import BeautifulSoup

class ColoQubePrinter:
    # Set hostname, display_name, and get status (for now)
    def __init__(self, hostname, display_name = None):
        """Object to encapsulate ColorQube web scraping and resulting data"""
        self.hostname = hostname
        self.status = None
        self.status_url = "http://{}/consumables.html".format(hostname)
        try:
            # Set display name based on response and if a display name was specified
            response = requests.get(self.status_url, timeout=1.5)
            status_html = response.content.decode('utf-8')
            if response.status_code != 200:
                self.display_name = hostname
            else:
                if display_name:
                    self.display_name = display_name
                else:
                    soup = BeautifulSoup(status_html, "html.parser")
                    title = soup.title.contents[0]
                    title = re.search("Supplies Status- (.+)", title)
                    if title:
                        self.display_name = title.groups(1)[0]
                    else:
                        self.display_name = hostname

            # Perform initial update
            self.update()
        except (requests.ConnectionError, requests.Timeout):
            self.display_name = self.hostname
            self.status = "Offline"

    def __str__(self):
        # Use ASCII escape codes to print out color based on status
        good_statuses = ["Ready", "Standby", "Power Saver Mode"]
        busy_statuses = ["Busy", "Initializing", "Warming Up", "Printing", "Cleaning"]
        if self.status in good_statuses:
            color = "\033[92m"
        elif self.status in busy_statuses:
            color = "\033[93m"
        else:
            color = "\033[91m"

        output = "{}{}:\n{}{}\n".format(color, self.display_name, self.status, "\033[0m")

        return output

    def update(self):
        """Update printer.status"""
        status_html = requests.get(self.status_url).content.decode('utf-8')
        match = re.search("([\w\s]+)(?:</a>)?</font>", status_html)
        if match:
            self.status = match.group(1).strip()
        else:
            self.status = None;

try:
    # Read printers from a file, printer.list, one line at a time
    printers = []
    with open("printers.list", "r") as printer_list:
        for hostname in printer_list.readlines():
            if hostname.strip():
                printers.append(hostname.strip())

    # Clear screen
    print("\033c")

    # Create objects and print status for each one
    for i in range(len(printers)):
        printers[i] = ColoQubePrinter(printers[i])
        print(printers[i])
except KeyboardInterrupt:
    print("Exiting...")
    sys.exit(1)
