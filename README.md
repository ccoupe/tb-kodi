# tb-kodi
A simple program that listens on a mqtt topic for a json payload
of `{"uri": "http://......}`. When it gets that it causes Kodi
to play the url. In this case it is a near real time mjpeg stream

Uses the pip kodijson library
