# DuetWebAPI
Python interface to Duet RepRap V2 or V3 firmware. 

* Works over IP network.  
* Does not support passwords on the printer. 
* Abstracts V2 to V3 differences. 
* NOT a general purpose interace; instead it has
  specific methods to issue commands or return
  information.  Adding new methods is encouraged,
  as long as they continue V2 V3 abstractaion.

# Install
* Download or clone the DuetWebAPI.py script. 
* Place it in the directory of the script that is going to include it, or in any directory in the python library path.

# Usage
* See 'testDWA.py' for examples. 
