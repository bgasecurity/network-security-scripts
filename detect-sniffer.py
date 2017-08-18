#!/usr/bin/env python


try:
        import re
        import sys
        import logging
        import argparse
        
        logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
        from scapy.all import *
except ImportError, err:
        print >> sys.stderr, "Error: {0}".format(err)
        sys.exit(1)   
   

class DetectSniffer(object):

        def __init__(self):

                self.__timeout = 1
                self.__fake_bcast="ff:ff:ff:ff:ff:fe"

                ip_regex = re.compile("^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$")
                net_regex = re.compile("^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/[0-9]{1,2}$")

                self.__ip_or_net = { ip_regex:self.__is_ip_sniffer, net_regex:self.__is_net_sniffer }


        def __is_net_sniffer(self, net):

                ans,unans = srp(Ether(dst = self.__fake_bcast)/ARP(pdst = net), 
                filter="arp and arp[7] = 2", timeout = self.__timeout, iface_hint = net) 
                
                ans = ARPingResult(ans.res, name = "bga.com.tr") 
                for snd,rcv in ans:
                        print rcv.sprintf("%ARP.psrc%")

    
        def __is_ip_sniffer(self, ip_address):

                responses = srp1(Ether(dst=self.__fake_bcast) / ARP(op="who-has", pdst=ip_address), type=ETH_P_ARP, iface_hint=ip_address, timeout=1, verbose=0) 

                if responses:
                        print "%s :OK"% (ip_address)
                else:
                        print "%s: NOT"% (ip_address)


        def _run(self, destination):

                for regex, func in self.__ip_or_net.iteritems():
                        if re.match(regex, destination):
                                func(destination)
                                break
                else:
                        print "Wrong Usage: {0}".format(destination)
                        sys.exit(1)

        

if __name__ == "__main__":
    
        description = "Detect Sniffer ..."
        usage = "Usage: use --help for further information"

        parser = argparse.ArgumentParser(description = description, usage = usage)
        parser.add_argument('-d', '--destination', dest='destination', help='Destination', required = True)
        args = parser.parse_args()

        destination = args.destination
        
        detect_sniffer = DetectSniffer()
        detect_sniffer._run(destination)
