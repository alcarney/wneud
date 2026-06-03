# wnued

(G)wneud -- v. to do / to make.


## Installing `systemd-python`

Since I use an image based OS, to get `systemd-python` installed I needed to

#. Use distrobox to spin up a fedora container
#. `dnf install git gcc systemd-devel`
#. git clone the repo and checkout v235
#. `uv build`
#. Install the wheel

To be improved...
