# Python Script containing a class to send commands to, and query specific information from,
#   Duet based printers running either Duet RepRap V2 or V3 firmware.
#
# Does NOT hold open the connection.  Use for low-volume requests.
# Does NOT, at this time, support Duet passwords.
#
# Not intended to be a gerneral purpose interface; instead, it contains methods
# to issue commands or return specific information. Feel free to extend with new
# methods for other information; please keep the abstraction for V2 V3 
#
# Copyright (C) 2020 Danal Estes all rights reserved.
# Released under The MIT License. Full text available via https://opensource.org/licenses/MIT
#
# Requires Python3

class DuetWebAPI:
    import requests
    import json
    import sys
    pt = 0
    _base_url = ''
    _login_url = ''


    def __init__(self,base_url,password):
        self._base_url = base_url
        try:
            _loginURL_=(f'{self._base_url}'+'/rr_connect?password='+password+'&time=00:00')
            r = self.requests.get(_loginURL_,timeout=(2,60))

            URL=(f'{self._base_url}'+'/rr_status?type=1')
            r = self.requests.get(URL,timeout=(2,60))
            j = self.json.loads(r.text)
            _=j['coords']
            self.pt = 2
            return
        except:
            try:
                URL=(f'{self._base_url}'+'/machine/status')
                r = self.requests.get(URL,timeout=(2,60))
                j = self.json.loads(r.text)
                _=j['result']
                self.pt = 3
                return
            except:
                print(self._base_url," does not appear to be a RRF2 or RRF3 printer", file=self.sys.stderr)
                return 
####
# The following methods are a more atomic, reading/writing basic data structures in the printer. 
####

    def printerType(self):
        return(self.pt)

    def baseURL(self):
        return(self._base_url)

    def getCoords(self):
        if (self.pt == 2):
            URL=(f'{self._base_url}'+'/rr_status?type=2')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            jc=j['coords']['xyz']
            an=j['axisNames']
            ret=self.json.loads('{}')
            for i in range(0,len(jc)):
                ret[ an[i] ] = jc[i]
            return(ret)
        if (self.pt == 3):
            URL=(f'{self._base_url}'+'/machine/status')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            ja=j['result']['move']['axes']
            jd=j['result']['move']['drives']
            ad=self.json.loads('{}')
            for i in range(0,len(ja)):
                ad[ ja[i]['letter'] ] = ja[i]['drives'][0]
            ret=self.json.loads('{}')
            for i in range(0,len(ja)):
                ret[ ja[i]['letter'] ] = jd[i]['position']
            return(ret)

    def getNumExtruders(self):
        if (self.pt == 2):
            URL=(f'{self._base_url}'+'/rr_status?type=2')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            jc=j['coords']['extr']
            return(len(jc))
        if (self.pt == 3):
            URL=(f'{self._base_url}'+'/machine/status')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            return(len(j['result']['move']['extruders']))

    def getNumTools(self):
        if (self.pt == 2):
            URL=(f'{self._base_url}'+'/rr_status?type=2')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            jc=j['tools']
            return(len(jc))
        if (self.pt == 3):
            URL=(f'{self._base_url}'+'/machine/status')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            return(len(j['result']['tools']))

    def getStatus(self):
        if (self.pt == 2):
            URL=(f'{self._base_url}'+'/rr_status?type=2')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            s=j['status']
            if ('I' in s): return('idle')
            if ('P' in s): return('processing')
            return(s)
        if (self.pt == 3):
            URL=(f'{self._base_url}'+'/machine/status')
            r = self.requests.get(URL)
            j = self.json.loads(r.text)
            return(j['result']['state']['status'])

    def gCode(self,command):
        if (self.pt == 2):
            URL=(f'{self._base_url}'+'/rr_gcode?gcode='+command)
            r = self.requests.get(URL)
        if (self.pt == 3):
            URL=(f'{self._base_url}'+'/machine/code/')
            r = self.requests.post(URL, data=command)
        if (r.ok):
           return(0)
        else:
            print("gCode command return code = ",r.status_code)
            print(r.reason)
            return(r.status_code)

    def getFilenamed(self,filename):
        if (self.pt == 2):
            URL=(f'{self._base_url}'+'/rr_download?name='+filename)
        if (self.pt == 3):
            URL=(f'{self._base_url}'+'/machine/file/'+filename)
        r = self.requests.get(URL)
        return(r.text.splitlines()) # replace('\n',str(chr(0x0a))).replace('\t','    '))

####
# The following methods provide services built on the atomics above. 
####


    # Given a line from config g that defines an endstop (N574) or Z probe (M558),
    # Return a line that will define the same thing to a "nil" pin, i.e. undefine it
    def _nilEndstop(self,configLine):
        ret = ''
        for each in [word for word in configLine.split()]: ret = ret + (each if (not (('P' in each[0]) or ('p' in each[0]))) else 'P"nil"') + ' '
        return(ret)

    def clearEndstops(self):
      c = self.getFilenamed('/sys/config.g')
      for each in [line for line in c if (('M574' in line) or ('M558' in line)                   )]: self.gCode(self._nilEndstop(each))

    def resetEndstops(self):
      c = self.getFilenamed('/sys/config.g')
      for each in [line for line in c if (('M574' in line) or ('M558' in line)                   )]: self.gCode(self._nilEndstop(each))
      for each in [line for line in c if (('M574' in line) or ('M558' in line) or ('G31' in line))]: self.gCode(each)

    def resetAxisLimits(self):
      c = self.getFilenamed('/sys/config.g')
      for each in [line for line in c if 'M208' in line]: self.gCode(each)
