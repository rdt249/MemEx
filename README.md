![drawing](https://scp-com.s3.amazonaws.com/314a1a15/University_of_Tennessee_at_Chattanooga_logo.svg.png)
<br>
![drawing](https://i.imgur.com/GIZFPgy.png)

# Memory Experiment (MemEx) v3

![drawing](http://freevector.co/wp-content/uploads/2014/02/56416-grid-or-visualization-option-circular-interface-button.png)

To ssh into the Raspberry Pi:
    1. Make sure you are using the UTC VPN (unless you're on campus).
    2. Open a new terminal and type `ssh pi@memex.research.utc.edu`
    3. Enter the password.

To update the github repository:
    1. Open a new terminal on the Pi (or ssh).
    2. If you are in the home directory (`cd ~`) run the command `MemEx/update_github`
    3. You could also run the command from the MemEx directory (`cd ~/MemEx`) with `./update_github`
    
To open a public Jupyter notebook:
    1. Open a new terminal on the Pi (or ssh).
    2. If you are in the home directory (`cd ~`) run the command `MemEx/public_notebook`
    3. You could also run the command from the MemEx directory (`cd ~/MemEx`) with `./public_notebook`
