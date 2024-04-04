# request_latency_tool

The tool is written in python and attempts to measure latency between two points on a network for:  TCP, DNS and HTTP. 

This is a first version, and has been succesfully used to try and pinpoint where latency issues are originating from on a complex network.

Of course this is only really effective at measuring latency between 2 endpoints (A and B), and if you are troubleshooting an application that goes through several proxies, (A, B, C, D) you will need to capture the information from different locations. With that in mind, this should really be seen as experimental for now. This was written quite quickly and has little in the form of exception handling but I did my best to ensure the program runs. I intend to enhance this in a future iteration once I have time and new ideas. Contributions and ideas are more than welcome. 
