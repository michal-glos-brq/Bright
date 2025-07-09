# Are you tired of manually clicking you adverserial hardware buttons on your monitor to adjust you brightness? I was! Now, you can simply run this very simple GUI app and do it in a nice, cozy GUI!

# Bright
Simple brightness controlling GUI for external monitors using ddcutil. <br>
Will discorover the monitors on it's own and provide the option to set their brightness from a GUI instead of the fucking hardware buttons ...

# Requirements
 - Require Python3.12+ (But would probably run on 3.5+)
 - Requires tkinter python library
 - Install ddcutil (see (install guide)[https://www.ddcutil.com/install/])

# How to install 
### Ubuntu:
```
# Install ddcutil
sudo add-apt-repository ppa:rockowitz/ddcutil
sudo apt-get update
# Install TKinter python module
pip3 install tkinter
# Install Bright
sudo cp ./bright /bin/bright
sudo chmod 777 /bin/bright
# Run
bright
```
