# Copyright (C) 2019  Nexedi SA and Contributors.
#                     Romain Courteaud <romain@nexedi.com>
#
# This program is free software: you can Use, Study, Modify and Redistribute
# it under the terms of the GNU General Public License version 3, or (at your
# option) any later version, as published by the Free Software Foundation.
#
# You can also Link and Combine this program with other software covered by
# the terms of any of the Free Software licenses or any of the Open Source
# Initiative approved licenses and Convey the resulting work. Corresponding
# source of such a combination shall include the source code for all other
# software used.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See COPYING file for full licensing terms.
# See https://www.nexedi.com/licensing for rationale and options.

import time
from .db import LogDB
from .configuration import createConfiguration, logConfiguration
from .status import logStatus, reportStatus
from .dns import (
    getReachableResolverList,
    expandDomainList,
    getDomainIpDict,
    reportDnsQuery,
    packDns,
    reverseIp,
)
from .domain import (
    queryWhois,
    reportWhoisQuery,
    packDomain,
)
from .http import (
    getRootUrl,
    getUrlHostname,
    checkHttpStatus,
    reportHttp,
    packHttp,
)
from .network import isTcpPortOpen, reportNetwork, packNetwork
import json
import email.utils
from collections import OrderedDict
from .ssl import (
    hasValidSSLCertificate,
    reportSslCertificate,
    packSslCertificate,
)
import datetime
from email.utils import parsedate_to_datetime
import tempfile
import os
import html


__version__ = "0.9.0"


class BotError(Exception):
    pass


def rfc822(date):
    return email.utils.format_datetime(date)


def _(string_to_escape):
    return html.escape("%s" % string_to_escape, quote=False)


def __(string_to_escape):
    return html.escape("%s" % string_to_escape, quote=True)


def dumpStatusDictToHTML(status_dict):
    body_result = "<main>"

    status_list = []
    append_status = status_list.append
    for table_key in status_dict:
        table = status_dict[table_key]
        if table:
            append_status(
                "<table><caption>%s</caption><thead><tr>" % _(table_key)
            )

            # Headers
            table_key_list = [x for x in table[0].keys()]
            table_key_list.sort()
            for table_key in table_key_list:
                append_status('<th scope="col">%s</th>' % _(table_key))
            append_status("</tr></thead><tbody>")

            # Status
            for line in table:
                append_status("<tr>")
                for table_key in table_key_list:
                    if table_key == "url":
                        append_status(
                            '<td><a href="%s">%s</a></td>'
                            % (__(line[table_key]), _(line[table_key]))
                        )
                    elif table_key in ("domain", "hostname"):
                        append_status(
                            '<td><a href="https://%s">%s</a></td>'
                            % (__(line[table_key]), _(line[table_key]))
                        )
                    else:
                        append_status("<td>%s</td>" % _(line[table_key]))
                append_status("</tr>")

            append_status("</tbody></table>")

    body_result += "\n".join(status_list)

    body_result += "</main>"

    result = (
        "<!DOCTYPE html><html><head>"
        '<meta name="viewport"\n'
        'content="width=device-width,height=device-height,'
        'initial-scale=1" />'
        "<title>Surykatka</title>"
        "<style>"
        "html {display: flex; justify-content: center;}\n"
        "body {width: 100%%; padding: 0 1em;"
        " word-break: break-all; display: flex;"
        " min-height: 100vh; flex-direction: column;}\n"
        "main {flex: 1;}\n"
        "html, body {height: 100%%; margin: 0;}\n"
        "table {border: 2px solid black; border-collapse: collapse;}\n"
        "caption {font-weight: bold;}\n"
        "th, td {border: 1px solid black; padding: 0 .5em}\n"
        "</style>\n"
        "</head><body>%(body)s</body></html>"
        % {
            "body": body_result,
        }
    )
    return result


def filterRecentStatus(status_dict, warning_period_duration):
    now = datetime.datetime.utcnow()

    del status_dict["bot_status"]
    del status_dict["warning"]
    del status_dict["missing_data"]

    for status_key in list(status_dict.keys()):
        for i in range(len(status_dict[status_key]) - 1, -1, -1):
            status_date = parsedate_to_datetime(
                status_dict[status_key][i]["date"]
            )
            if (warning_period_duration) < (now - status_date).total_seconds():
                del status_dict[status_key][i]

        status_dict[status_key].sort(
            key=lambda x: parsedate_to_datetime(x["date"])
        )

        if not status_dict[status_key]:
            del status_dict[status_key]


def filterWarningStatus(
    status_dict,
    interval,
    not_critical_url_list,
    warning_period_duration,
    keep_warning=True,
):
    now = datetime.datetime.utcnow()
    if interval < 60:
        interval = 60
    for i in range(len(status_dict["bot_status"]) - 1, -1, -1):
        status_date = parsedate_to_datetime(
            status_dict["bot_status"][i]["date"]
        )
        if (now - status_date).total_seconds() < (2 * interval):
            # Skip the bot status if it was recently triggerer
            del status_dict["bot_status"][i]
    if not status_dict["bot_status"]:
        del status_dict["bot_status"]

    if (not status_dict["warning"]) or (not keep_warning):
        del status_dict["warning"]

    for i in range(len(status_dict["whois"]) - 1, -1, -1):
        expiration_date = status_dict["whois"][i]["expiration_date"]
        if (expiration_date is None) or (
            (expiration_date is not None)
            and (
                (warning_period_duration)
                < (
                    parsedate_to_datetime(expiration_date) - now
                ).total_seconds()
            )
        ):
            # Not handled whois entry hidden. Only check DNS warning in such case
            # Warn 2 weeks before expiration
            del status_dict["whois"][i]
        else:
            # Drop columns with too much info
            del status_dict["whois"][i]["registrar"]
            del status_dict["whois"][i]["whois_server"]
            del status_dict["whois"][i]["creation_date"]
            del status_dict["whois"][i]["updated_date"]
            del status_dict["whois"][i]["name_servers"]
            del status_dict["whois"][i]["whois_status"]
            del status_dict["whois"][i]["emails"]
            del status_dict["whois"][i]["dnssec"]
            del status_dict["whois"][i]["name"]
            del status_dict["whois"][i]["org"]
            del status_dict["whois"][i]["address"]
            del status_dict["whois"][i]["city"]
            del status_dict["whois"][i]["state"]
            del status_dict["whois"][i]["zipcode"]
            del status_dict["whois"][i]["country"]

    if not status_dict["whois"]:
        del status_dict["whois"]

    for i in range(len(status_dict["dns_server"]) - 1, -1, -1):
        state = status_dict["dns_server"][i]["state"]
        if state == "open":
            del status_dict["dns_server"][i]
    if not status_dict["dns_server"]:
        del status_dict["dns_server"]

    mx_domain_dict = {}
    a_and_aaaa_domain_set = set()
    for i in range(len(status_dict["dns_query"]) - 1, -1, -1):
        state = status_dict["dns_query"][i]["response"]
        if state == "":
            if status_dict["dns_query"][i]["rdtype"] in ("MX", "TXT", "PTR"):
                # No MX/TXT/PTR is allowed
                # XXX report empty SPF!
                del status_dict["dns_query"][i]
        else:
            # Keep track of possible domain handling MX
            if status_dict["dns_query"][i]["rdtype"] == "MX":
                for mx_domain in state.split(", "):
                    mx_domain_dict[mx_domain] = True

            if status_dict["dns_query"][i]["rdtype"] in ("A", "AAAA"):
                a_and_aaaa_domain_set.add(
                    status_dict["dns_query"][i]["domain"]
                )

            del status_dict["dns_query"][i]

    # Loop once more to remove empty entries for domain for which there is a valid entry
    # for instance if A is present and no AAAA and the reverse
    for i in range(len(status_dict["dns_query"]) - 1, -1, -1):
        if (
            status_dict["dns_query"][i]["rdtype"] in ("A", "AAAA")
            and status_dict["dns_query"][i]["response"] == ""
            and status_dict["dns_query"][i]["domain"] in a_and_aaaa_domain_set
        ):
            del status_dict["dns_query"][i]

    if not status_dict["dns_query"]:
        del status_dict["dns_query"]

    if not status_dict["missing_data"]:
        del status_dict["missing_data"]

    for i in range(len(status_dict["tcp_server"]) - 1, -1, -1):
        state = status_dict["tcp_server"][i]["state"]
        # Skip if all domains lead to not critical urls
        prefix = ""
        if status_dict["tcp_server"][i]["port"] == 80:
            prefix = "http://"
        elif status_dict["tcp_server"][i]["port"] == 443:
            prefix = "https://"
        elif status_dict["tcp_server"][i]["port"] == 25:
            prefix = "smtp://"
        else:
            raise NotImplementedError(
                "Not supported server port %i"
                % status_dict["tcp_server"][i]["port"]
            )
        domain_list = status_dict["tcp_server"][i]["domain"].split(", ")
        domain_list = [
            x
            for x in domain_list
            if "%s%s/" % (prefix, x) not in not_critical_url_list
        ]
        if status_dict["tcp_server"][i]["port"] == 25:
            has_intersection = (
                len(set(mx_domain_dict.keys()).intersection(domain_list)) != 0
            )
            if ((state == "open") and has_intersection) or (
                (state != "open") and (not has_intersection)
            ):
                # if one MX points to this server, port should be open
                # if no MX points to this serverm port should NOT be open
                del status_dict["tcp_server"][i]
        elif (state == "open") or (not domain_list):
            del status_dict["tcp_server"][i]
    if not status_dict["tcp_server"]:
        del status_dict["tcp_server"]

    for i in range(len(status_dict["ssl_certificate"]) - 1, -1, -1):
        not_after = status_dict["ssl_certificate"][i]["not_after"]
        if (
            (not_after is not None)
            and (
                (warning_period_duration)
                < (parsedate_to_datetime(not_after) - now).total_seconds()
            )
        ) or (
            ("https://%s/" % status_dict["ssl_certificate"][i]["hostname"])
            in not_critical_url_list
        ):
            # Warn 2 weeks before expiration
            # Skip if we check only the http url
            del status_dict["ssl_certificate"][i]
        else:
            # Drop columns with too much info
            del status_dict["ssl_certificate"][i]["not_before"]
            del status_dict["ssl_certificate"][i]["issuer"]
            del status_dict["ssl_certificate"][i]["sha1_fingerprint"]
            del status_dict["ssl_certificate"][i]["subject"]
    if not status_dict["ssl_certificate"]:
        del status_dict["ssl_certificate"]

    for i in range(len(status_dict["http_query"]) - 1, -1, -1):
        http_code = status_dict["http_query"][i]["status_code"]
        if (http_code != 404) and (http_code < 500):
            del status_dict["http_query"][i]
        elif status_dict["http_query"][i]["url"] in not_critical_url_list:
            del status_dict["http_query"][i]
        else:
            # Drop columns with too much info
            del status_dict["http_query"][i]["http_header_dict"]
            del status_dict["http_query"][i]["total_seconds"]
    if not status_dict["http_query"]:
        del status_dict["http_query"]


class WebBot:
    def __init__(self, **kw):
        self.config_kw = kw
        self.config = createConfiguration(**kw)

    def closeDB(self):
        if hasattr(self, "_db"):
            self._db.close()

    def initDB(self):
        self._db = LogDB(self.config["SQLITE"])
        self._db.createTables()

    def calculateUrlList(self):
        return self.config["URL"].split()

    def calculateFullDomainList(self):
        # Calculate the full list of domain to check
        domain_list = self.config["DOMAIN"].split()

        # Extract the list of URL domains
        url_list = self.calculateUrlList()
        for url in url_list:
            domain = getUrlHostname(url)
            if domain is not None:
                domain_list.append(domain)
        domain_list = list(set(domain_list))

        # Expand with all parent domains
        return expandDomainList(
            domain_list,
            public_suffix_list=self.config["PUBLIC_SUFFIX"].split(),
        )

    def calculateWhoisDomainList(self, domain_list):
        # Calculate the top domain for whois
        domain_list = domain_list.copy()
        domain_list.sort(key=lambda x: x.count("."))
        i = 0
        while i < len(domain_list):
            base_domain = ".%s" % domain_list[i]
            j = i + 1
            while j < len(domain_list):
                sub_domain = domain_list[j]
                if sub_domain.endswith(base_domain):
                    domain_list.pop(j)
                else:
                    j += 1
            i += 1

        return domain_list

    def calculateNotCriticalUrlList(self):
        domain_list = self.config["DOMAIN"].split()
        url_list = self.config["URL"].split()
        not_critical_url_list = []
        for url in url_list:
            hostname = getUrlHostname(url)
            if hostname is not None:
                if hostname not in domain_list:
                    # Domain not explicitely checked
                    # Skip both root url
                    for protocol in ("http", "https"):
                        not_critical_url = "%s://%s/" % (protocol, hostname)
                        if not_critical_url not in url_list:
                            not_critical_url_list.append(not_critical_url)
        return not_critical_url_list

    def iterateLoop(self):
        status_id = logStatus(self._db, "loop")

        if self.config["RELOAD"] == "True":
            self.config = createConfiguration(**self.config_kw)

        timeout = int(self.config["TIMEOUT"])
        elapsed_fast = float(self.config["ELAPSED_FAST"])
        elapsed_moderate = float(self.config["ELAPSED_MODERATE"])
        contact = self.config["CONTACT"]
        # logPlatform(self._db, __version__, status_id)

        # Get list of all domains
        domain_list = self.calculateFullDomainList()
        whois_domain_list = self.calculateWhoisDomainList(domain_list)

        for whois_domain in whois_domain_list:
            queryWhois(self._db, status_id, whois_domain)

        # Calculate the resolver list
        resolver_ip_list = getReachableResolverList(
            self._db, status_id, self.config["NAMESERVER"].split(), timeout
        )
        if not resolver_ip_list:
            return

        # Get the list of server to check
        # XXX Check DNS expiration
        server_ip_dict = getDomainIpDict(
            self._db, status_id, resolver_ip_list, domain_list, "A", timeout
        )
        server_ip_dict.update(
            **getDomainIpDict(
                self._db,
                status_id,
                resolver_ip_list,
                domain_list,
                "AAAA",
                timeout,
            )
        )
        # Check the mail configuration for every domain (MX and SPF)
        getDomainIpDict(
            self._db, status_id, resolver_ip_list, domain_list, "MX", timeout
        )
        # Check the mail configuration for every domain (MX and SPF)
        getDomainIpDict(
            self._db, status_id, resolver_ip_list, domain_list, "TXT", timeout
        )

        # Query PTR record
        getDomainIpDict(
            self._db,
            status_id,
            resolver_ip_list,
            [reverseIp(x) for x in server_ip_dict.keys()],
            "PTR",
            timeout,
        )

        # Check TCP port for the list of IP found
        # XXX For now, check http/https only
        server_ip_list = [x for x in server_ip_dict.keys()]
        url_dict = {}
        for server_ip in server_ip_list:
            # XXX Check SSL certificate expiration
            for port, protocol in [
                (80, "http"),
                (443, "https"),
                (25, "smtp"),
            ]:
                if isTcpPortOpen(
                    self._db, server_ip, port, status_id, timeout
                ):
                    for hostname in server_ip_dict[server_ip]:
                        if port in [443, 587]:
                            # Store certificate information
                            if not hasValidSSLCertificate(
                                self._db,
                                server_ip,
                                port,
                                hostname,
                                status_id,
                                timeout,
                            ):
                                # If certificate is not valid,
                                # no need to do another query
                                continue
                        url = "%s://%s/" % (protocol, hostname)
                        if url not in url_dict:
                            url_dict[url] = []
                        url_dict[url].append(server_ip)

        # XXX put back orignal url list
        for url in self.calculateUrlList():
            if url not in url_dict:
                root_url = getRootUrl(url)
                if root_url in url_dict:
                    url_dict[url] = url_dict[root_url]

        # Check HTTP Status
        for url in url_dict:
            if url.startswith("smtp"):
                # XXX TODO implement smtp connection check
                continue
            for ip in url_dict[url]:
                checkHttpStatus(
                    self._db,
                    status_id,
                    url,
                    ip,
                    __version__,
                    contact,
                    timeout,
                    elapsed_fast,
                    elapsed_moderate,
                )
                # XXX Check location header and check new url recursively
                # XXX Parse HTML, fetch found link, css, js, image
                # XXX Check HTTP Cache

    def status(self):
        result_dict = OrderedDict()

        # Report the bot status
        result_dict["bot_status"] = []
        try:
            bot_status = reportStatus(self._db).get()
        except self._db.Status.DoesNotExist:
            result_dict["bot_status"].append(
                {"text": "", "date": rfc822(datetime.datetime.utcnow())}
            )
        else:
            result_dict["bot_status"].append(
                {"text": bot_status.text, "date": rfc822(bot_status.timestamp)}
            )

        domain_list = self.calculateFullDomainList()
        whois_domain_list = self.calculateWhoisDomainList(domain_list)

        # Report list of Whois query
        query = reportWhoisQuery(self._db, domain=whois_domain_list)
        result_dict["whois"] = []
        for domain_change in query.dicts().iterator():
            result_dict["whois"].append(
                {
                    "domain": domain_change["domain"],
                    "date": rfc822(domain_change["status"]),
                    "registrar": domain_change["registrar"],
                    "whois_server": domain_change["whois_server"],
                    "creation_date": (
                        rfc822(domain_change["creation_date"])
                        if (
                            type(domain_change["creation_date"])
                            is datetime.datetime
                        )
                        else None
                    ),
                    "updated_date": (
                        rfc822(domain_change["updated_date"])
                        if (
                            type(domain_change["updated_date"])
                            is datetime.datetime
                        )
                        else None
                    ),
                    "expiration_date": (
                        rfc822(domain_change["expiration_date"])
                        if (
                            type(domain_change["expiration_date"])
                            is datetime.datetime
                        )
                        else None
                    ),
                    "name_servers": domain_change["name_servers"],
                    "whois_status": domain_change["whois_status"],
                    "emails": domain_change["emails"],
                    "dnssec": domain_change["dnssec"],
                    "name": domain_change["name"],
                    "org": domain_change["org"],
                    "address": domain_change["address"],
                    "city": domain_change["city"],
                    "state": domain_change["state"],
                    "zipcode": domain_change["zipcode"],
                    "country": domain_change["country"],
                }
            )

        # Report the list of DNS server status
        checked_resolver_ip_dict = {}
        query = reportNetwork(
            self._db,
            port="53",
            transport="UDP",
            ip=self.config["NAMESERVER"].split(),
        )
        resolver_ip_list = []
        result_dict["dns_server"] = []
        for network_change in query.dicts().iterator():
            checked_resolver_ip_dict[network_change["ip"]] = True
            if network_change["state"] == "open":
                resolver_ip_list.append(network_change["ip"])
            result_dict["dns_server"].append(
                {
                    "ip": network_change["ip"],
                    "state": network_change["state"],
                    "date": rfc822(network_change["status"]),
                }
            )

        result_dict["missing_data"] = []
        for resolver_ip in self.config["NAMESERVER"].split():
            if resolver_ip not in checked_resolver_ip_dict:
                result_dict["missing_data"].append(
                    {
                        "text": resolver_ip,
                        "date": result_dict["bot_status"][0]["date"],
                    }
                )

        checked_domain_dict = {}
        # Report list of DNS query
        query = reportDnsQuery(
            self._db,
            domain=domain_list,
            resolver_ip=resolver_ip_list,
            rdtype=["A", "AAAA", "MX", "TXT"],
        )
        server_ip_dict = {}
        result_dict["dns_query"] = []
        result_dict["warning"] = []
        for dns_change in query.dicts().iterator():

            if dns_change["domain"] not in checked_domain_dict:
                checked_domain_dict[dns_change["domain"]] = {}
            if (
                not dns_change["rdtype"]
                in checked_domain_dict[dns_change["domain"]]
                or not checked_domain_dict[dns_change["domain"]][
                    dns_change["rdtype"]
                ]["response"]
            ):
                checked_domain_dict[dns_change["domain"]][
                    dns_change["rdtype"]
                ] = dns_change
            elif dns_change["response"]:
                # Case IP has been provided by both dns:
                checked_domain_dict[dns_change["domain"]][
                    dns_change["rdtype"]
                ]["resolver_ip"] += (", " + dns_change["resolver_ip"])
                checked_domain_dict[dns_change["domain"]][
                    dns_change["rdtype"]
                ]["response"] += (", " + dns_change["response"])

            result_dict["dns_query"].append(
                {
                    "domain": dns_change["domain"],
                    "rdtype": dns_change["rdtype"],
                    "resolver_ip": dns_change["resolver_ip"],
                    "date": rfc822(dns_change["status"]),
                    "response": dns_change["response"],
                }
            )

        for domain in domain_list:
            if domain in checked_domain_dict:
                if (
                    "A" in checked_domain_dict[domain]
                    or "AAAA" in checked_domain_dict[domain]
                ):
                    domain_server_ip_list = []
                    for ip_record in ("A", "AAAA"):
                        if ip_record in checked_domain_dict[domain]:
                            # Drop empty response
                            domain_server_ip_list += [
                                x
                                for x in checked_domain_dict[domain][
                                    ip_record
                                ]["response"].split(", ")
                                if x
                            ]
                    if len(domain_server_ip_list) == 1:
                        result_dict["warning"].append(
                            {
                                "text": "(A) single IP for: %s" % (domain,),
                                "date": result_dict["bot_status"][0]["date"],
                            }
                        )

                    for server_ip in domain_server_ip_list:
                        if server_ip not in server_ip_dict:
                            server_ip_dict[server_ip] = []
                        if domain not in server_ip_dict[server_ip]:
                            server_ip_dict[server_ip].append(domain)
                else:
                    result_dict["missing_data"].append(
                        {
                            "text": "(A) " + domain,
                            "date": result_dict["bot_status"][0]["date"],
                        }
                    )

                if "MX" in checked_domain_dict[domain]:
                    if checked_domain_dict[domain]["MX"]["response"]:
                        for mx_domain in checked_domain_dict[domain]["MX"][
                            "response"
                        ].split(", "):
                            if mx_domain not in checked_domain_dict:
                                result_dict["missing_data"].append(
                                    {
                                        "text": "(MX "
                                        + domain
                                        + ") "
                                        + mx_domain,
                                        "date": result_dict["bot_status"][0][
                                            "date"
                                        ],
                                    }
                                )
                else:
                    result_dict["missing_data"].append(
                        {
                            "text": "(MX) " + domain,
                            "date": result_dict["bot_status"][0]["date"],
                        }
                    )

                if "TXT" in checked_domain_dict[domain]:
                    if (
                        '"v=spf'
                        not in checked_domain_dict[domain]["TXT"]["response"]
                    ):
                        result_dict["warning"].append(
                            {
                                "text": "(No spf configured: %s) "
                                % str(
                                    checked_domain_dict[domain]["TXT"][
                                        "response"
                                    ]
                                )
                                + domain,
                                "date": rfc822(
                                    checked_domain_dict[domain]["TXT"][
                                        "status"
                                    ]
                                ),
                            }
                        )
                else:
                    result_dict["missing_data"].append(
                        {
                            "text": "(TXT) " + domain,
                            "date": result_dict["bot_status"][0]["date"],
                        }
                    )

            else:
                result_dict["missing_data"].append(
                    {
                        "text": domain,
                        "date": result_dict["bot_status"][0]["date"],
                    }
                )

        # Report PTR
        # Report list of DNS query
        query = reportDnsQuery(
            self._db,
            domain=[reverseIp(x) for x in server_ip_dict.keys()],
            resolver_ip=resolver_ip_list,
            rdtype=["PTR"],
        )
        for dns_change in query.dicts().iterator():
            # XXX Duplicated code
            result_dict["dns_query"].append(
                {
                    "domain": dns_change["domain"],
                    "rdtype": dns_change["rdtype"],
                    "resolver_ip": dns_change["resolver_ip"],
                    "date": rfc822(dns_change["status"]),
                    "response": dns_change["response"],
                }
            )

        # Report the list of CDN status
        query = reportNetwork(
            self._db,
            port=["80", "443", "25"],
            transport="TCP",
            ip=[x for x in server_ip_dict.keys()],
        )
        url_dict = {}
        result_dict["tcp_server"] = []
        for network_change in query.dicts().iterator():
            result_dict["tcp_server"].append(
                {
                    "ip": network_change["ip"],
                    "state": network_change["state"],
                    "port": network_change["port"],
                    "date": rfc822(network_change["status"]),
                    "domain": ", ".join(server_ip_dict[network_change["ip"]]),
                }
            )
            if network_change["state"] == "open":
                for hostname in server_ip_dict[network_change["ip"]]:
                    protocol = {80: "http", 443: "https", 25: "smtp"}[
                        network_change["port"]
                    ]
                    # Chrome automatically add the trailing /
                    # when user enter the domain name
                    url = "%s://%s/" % (protocol, hostname)
                    if url not in url_dict:
                        url_dict[url] = []
                    url_dict[url].append(network_change["ip"])

        # Report the SSL status
        result_dict["ssl_certificate"] = []
        for ip_, domain_list_ in server_ip_dict.items():
            query = reportSslCertificate(
                self._db,
                ip=ip_,
                port=443,
                hostname=domain_list_,
            )
            for ssl_certificate in query.dicts().iterator():
                result_dict["ssl_certificate"].append(
                    {
                        "hostname": ssl_certificate["hostname"],
                        "ip": ssl_certificate["ip"],
                        "port": ssl_certificate["port"],
                        "sha1_fingerprint": ssl_certificate[
                            "sha1_fingerprint"
                        ],
                        "subject": ssl_certificate["subject"],
                        "issuer": ssl_certificate["issuer"],
                        "not_before": (
                            rfc822(ssl_certificate["not_before"])
                            if (ssl_certificate["not_before"] is not None)
                            else None
                        ),
                        "not_after": (
                            rfc822(ssl_certificate["not_after"])
                            if (ssl_certificate["not_after"] is not None)
                            else None
                        ),
                        "date": rfc822(ssl_certificate["status"]),
                    }
                )

        # XXX put back orignal url list
        for url in self.calculateUrlList():
            if url not in url_dict:
                root_url = getRootUrl(url)
                if root_url in url_dict:
                    url_dict[url] = url_dict[root_url]

        # map IP to URLs for less queries during fetching results
        ip_to_url_dict = {}
        for url, ip_list in url_dict.items():
            for ip in ip_list:
                ip_to_url_dict.setdefault(ip, [])
                if url not in ip_to_url_dict[ip]:
                    ip_to_url_dict[ip].append(url)

        # Get the list of HTTP servers to check
        result_dict["http_query"] = []
        missing_url_list = []
        for ip, url_list in ip_to_url_dict.items():
            query = reportHttp(self._db, ip=ip, url=url_list)
            for network_change in query.dicts().iterator():

                # Confirm that redirection url are checked
                if network_change["status_code"] in (301, 302, 303):
                    # XXX check full url
                    redirect_url = network_change["http_header_dict"][
                        "Location"
                    ]

                    if (redirect_url not in url_dict) and (
                        redirect_url not in missing_url_list
                    ):
                        missing_url_list.append(redirect_url)
                        result_dict["warning"].append(
                            {
                                "text": "(Not checked URL %s ->) %s"
                                % (network_change["url"], redirect_url),
                                "date": rfc822(network_change["status"]),
                            }
                        )

                # Check HTTP CSP header
                if network_change["status_code"] != 524:
                    # Skip timeout
                    # check missing import headers
                    if (
                        "Content-Type"
                        not in network_change["http_header_dict"]
                    ):
                        if (
                            network_change["http_header_dict"].get(
                                "Content-Length", 0
                            )
                            != 0
                        ):
                            result_dict["warning"].append(
                                {
                                    "text": "(No Content-Type header) %s"
                                    % (network_change["url"],),
                                    "date": rfc822(network_change["status"]),
                                }
                            )
                    elif network_change["http_header_dict"][
                        "Content-Type"
                    ].startswith("text/html"):
                        if (
                            "Content-Security-Policy"
                            not in network_change["http_header_dict"]
                        ) and (
                            network_change["status_code"]
                            not in (301, 302, 303)
                        ):
                            # In case of redirection, CSP is not needed
                            # as the browser will not render the page
                            result_dict["warning"].append(
                                {
                                    "text": "(No Content-Security-Policy header) %s"
                                    % (network_change["url"],),
                                    "date": rfc822(network_change["status"]),
                                }
                            )

                result_dict["http_query"].append(
                    {
                        "status_code": network_change["status_code"],
                        "http_header_dict": network_change["http_header_dict"],
                        "total_seconds": network_change["total_seconds"],
                        "url": network_change["url"],
                        "ip": network_change["ip"],
                        "date": rfc822(network_change["status"]),
                    }
                )

        return result_dict

    def stop(self):
        self._running = False
        logStatus(self._db, "stop")

    def crawl(self):
        status_id = logStatus(self._db, "start")
        logConfiguration(self._db, status_id, self.config)

        self._running = True
        try:
            while self._running:
                previous_time = datetime.datetime.utcnow()
                self.iterateLoop()
                next_time = datetime.datetime.utcnow()
                interval = int(self.config.get("INTERVAL"))
                if interval < 0:
                    self.stop()
                else:
                    time.sleep(
                        max(
                            0,
                            interval
                            - (next_time - previous_time).total_seconds(),
                        )
                    )
        except KeyboardInterrupt:
            self.stop()
        except:
            # XXX Put traceback in the log?
            logStatus(self._db, "error")
            raise

    def pack(self):
        logStatus(self._db, "packing")
        packDns(self._db)
        packDomain(self._db)
        packHttp(self._db)
        packNetwork(self._db)
        packSslCertificate(self._db)
        self._db.vacuum()
        logStatus(self._db, "packed")

    def run(self, mode):
        status_dict = None
        if mode not in [
            "crawl",
            "pack",
            "status",
            "recent",
            "warning",
            "error",
        ]:
            raise NotImplementedError("Unexpected mode: %s" % mode)

        if self.config["SQLITE"] == ":memory:":
            # Crawl/report are mandatory when using memory
            if mode == "warning":
                mode = "wallwarning"
            elif mode == "error":
                mode = "wallerror"
            elif mode == "recent":
                mode = "wallrecent"
            else:
                mode = "all"

        self.initDB()

        try:
            if mode in [
                "crawl",
                "wallwarning",
                "wallerror",
                "wallrecent",
                "all",
            ]:
                self.crawl()
            if mode in [
                "status",
                "all",
                "wallwarning",
                "warning",
                "wallerror",
                "error",
                "wallrecent",
                "recent",
            ]:
                status_dict = self.status()
            if mode == "pack":
                self.pack()
        except:
            self.closeDB()
            raise
        else:
            self.closeDB()

        if status_dict is not None:
            if mode in ("wallwarning", "warning", "wallerror", "error"):
                filterWarningStatus(
                    status_dict,
                    int(self.config.get("INTERVAL")),
                    self.calculateNotCriticalUrlList(),
                    float(self.config["WARNING_PERIOD"]),
                    keep_warning=("warning" in mode),
                )
            elif mode in ("wallrecent", "recent"):
                filterRecentStatus(
                    status_dict,
                    float(self.config["WARNING_PERIOD"]),
                )
            if self.config["FORMAT"] == "json":
                status_output = json.dumps(status_dict)
            elif self.config["FORMAT"] == "html":
                status_output = dumpStatusDictToHTML(status_dict)
            else:
                status_list = []
                append_status = status_list.append
                for table_key in status_dict:
                    append_status("# %s" % table_key)
                    append_status("")
                    table = status_dict[table_key]
                    if table:
                        # Print the header
                        table_key_list = [x for x in table[0].keys()]
                        table_key_list.sort()
                        append_status(" | ".join(table_key_list))
                        for line in table:
                            append_status(
                                " | ".join(
                                    ["%s" % (line[x]) for x in table_key_list]
                                )
                            )
                        append_status("")
                status_output = "\n".join(status_list)
            if self.config["STDOUT"] == "":
                print(status_output)
            else:
                # https://blog.gocept.com/2013/07/15/reliable-file-updates-with-python/#write-replace
                with tempfile.NamedTemporaryFile(
                    "w",
                    dir=os.path.dirname(self.config["STDOUT"]),
                    delete=False,
                ) as temp_file:
                    temp_file.write(status_output)
                    temp_file_name = temp_file.name
                os.rename(temp_file_name, self.config["STDOUT"])


def create_bot(**kw):
    return WebBot(**kw)
