# README.md
Wakesys waits for a mqtt signal from another system, changes the current linux system from it's sleeping state by some kind of simulated mouse movement and and prepares this system to 'do something' with the payload argument If the payload is 'uri': <a video url> then a video player is launched to start that (presumably on a newly awakened monitor)

### ~/Projects/iot/wakesys
- started from systemd. So, we have root priv. But we start after there is a GUI started. and after the network is up. 
- need a directory to run from (assuming python). /usr/local/lib/wakesys/wakesys.sh.   wakesys.service stored in /etc/systemd/system
- mqtt topic is 'homie/<node>/doorbell/cmd/set' json payload = {"uri": string } or {"off": "off"}
- how to 'unblank' the screen (hdmi TV) X11 and wayland
	- xrandr
	- sddm : `sudo systemctl restart display-manager` and `man sddm.conf`
	- Auto login with SDDM can be done via the sddm.conf User= setting
	- KDE screensaver [reddit tips](https://www.reddit.com/r/kde/comments/1q1g3nr/still_no_way_to_get_screensavers/). The one about video screen saver might be more useful for zmqtracker.
	- xset is the X11 hero/villan
	- use jiggler' script
		- `echo $XDG_SESSION_TYPE`
		- For "x11"
			-
			  ```
			  while true; do
			    xdotool mousemove_relative 1 1
			    sleep 60
			    xdotool mousemove_relative -- -1 -1
			    sleep 60
			  done
			  ```
		- For "wayland"
			- `ydotool mousemove 50 50`
		- For "tty" - yes that is a real value, probably useful
	- end an mqtt message {"cmd": "prepare"|"start"|"stop"}
		- when prepare is received, do mouse jiggle thing and load/start app