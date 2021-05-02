<h1 align="center" style="color:white; background-color:black">LiveFeed</h1>
<h4 align="center">A simple LoRa Image Transmiter</h4>

<p align="center">
	<a href="http://zenith.eesc.usp.br/">
    <img src="https://img.shields.io/badge/Zenith-Embarcados-black?style=for-the-badge"/>
    </a>
    <a href="https://eesc.usp.br/">
    <img src="https://img.shields.io/badge/Linked%20to-EESC--USP-black?style=for-the-badge"/>
    </a>
    <a href="https://github.com/zenitheesc/livefeed/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/zenitheesc/livefeed?style=for-the-badge"/>
    </a>
    <a href="https://github.com/zenitheesc/livefeed/issues">
    <img src="https://img.shields.io/github/issues/zenitheesc/livefeed?style=for-the-badge"/>
    </a>
    <a href="https://github.com/zenitheesc/livefeed/commits/main">
    <img src="https://img.shields.io/github/commit-activity/m/zenitheesc/livefeed?style=for-the-badge">
    </a>
    <a href="https://github.com/zenitheesc/livefeed/graphs/contributors">
    <img src="https://img.shields.io/github/contributors/zenitheesc/livefeed?style=for-the-badge"/>
    </a>
    <a href="https://github.com/zenitheesc/livefeed/commits/main">
    <img src="https://img.shields.io/github/last-commit/zenitheesc/livefeed?style=for-the-badge"/>
    </a>
    <a href="https://github.com/zenitheesc/livefeed/issues">
    <img src="https://img.shields.io/github/issues-raw/zenitheesc/livefeed?style=for-the-badge" />
    </a>
    <a href="https://github.com/zenitheesc/livefeed/pulls">
    <img src = "https://img.shields.io/github/issues-pr-raw/zenitheesc/livefeed?style=for-the-badge">
    </a>
</p>

<p align="center">
    <a href="#environment-and-tools">Environment and Tools</a> •
    <a href="#steps-to-run-and-debug">Steps to run and debug</a> 
</p>

## Environment and tools

LiveFeed is a software project aimed to send images, in real-time, from the probe to our Ground Station. In the development, we used a **Raspberry Pi model 3B** in the probe, as well as an **8MP Raspberry Pi Camera** with a 160º wide-angle lens. The Raspberry Pi had to capture, compress and send the images during the flight. 

For transmitting this data via radio-frequency (RF), we used a chip with **LoRa** technology, SX127x, widely employed on Internet of Things (IoT) applications. In our Ground Station, another Raspberry Pi and LoRa chip were receiving the signal with a Yagi antenna. 

Experimentally, the system developed worked well with the probe on the ground and close to the basis, a few tens of meters. But the system stopped working when the probe ascended to higher altitudes, because the receiver lost communication, due to the low power used in the transmission, combined with low-gain antennas. Nevertheless, this subproject has been shown innovative and promising, challenging the group to improve its performance for the next flight, creating a reliable image transmitting system. 

## Steps to run and debug

In order to run this project, you must have two Raspberry Pi, two SX127x, and a Raspberry Pi Camera. One Raspberry Pi must be connected to the SX127x to be the Ground Station and the other one must be connected to the other SX127x and the Raspberry Pi Camera. 

Moreover, both Raspberry Pi must have [Python2](https://www.python.org/downloads/) and all dependencies installed.

In the Ground Station, run the command:

```
python2 receiver.py
```

And in the other Raspberry Pi, run the command:

```
python2 transmission.py
```
---

<p align="center">
    <a href="http://zenith.eesc.usp.br">
    <img src="https://img.shields.io/badge/Check%20out-Zenith's Oficial Website-black?style=for-the-badge" />
    </a> 
    <a href="https://www.facebook.com/zenitheesc">
    <img src="https://img.shields.io/badge/Like%20us%20on-facebook-blue?style=for-the-badge"/>
    </a> 
    <a href="https://www.instagram.com/zenith_eesc/">
    <img src="https://img.shields.io/badge/Follow%20us%20on-Instagram-red?style=for-the-badge"/>
    </a>

</p>
<p align = "center">
<a href="zenith.eesc@gmail.com">zenith.eesc@gmail.com</a>
</p>
