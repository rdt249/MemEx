<b> University of Tennessee at Chattanooga </b> <br>
<b> Reliable Electronics and Systems Lab </b>
### Memory Experiment (MemEx) v3

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
