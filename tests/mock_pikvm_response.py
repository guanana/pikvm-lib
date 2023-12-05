pikvm_mock_info = """{
    "ok": true,
    "result": {
        "extras": { 
            "ipmi": {
                "daemon": "kvmd-ipmi",
                "description": "Show IPMI information",
                "enabled": true,
                "icon": "share/svg/ipmi.svg",
                "keyboard_cap": false,
                "name": "IPMI",
                "path": "ipmi",
                "place": 21,
                "port": 623
            },
            "vnc": {
                "daemon": "kvmd-vnc",
                "description": "Show VNC information",
                "enabled": true,
                "icon": "share/svg/vnc.svg",
                "keyboard_cap": false,
                "name": "VNC",
                "path": "vnc",
                "place": 20,
                "port": 5900
            }
        },
        "hw": { 
            "health": {
                "temp": {
                    "cpu": 36.511, 
                    "gpu": 35.0 
                },
                "throttling": {
                    "parsed_flags": {
                        "freq_capped": {
                            "now": false,
                            "past": false
                        },
                        "throttled": {
                            "now": false,
                            "past": false
                        },
                        "undervoltage": {
                            "now": false,
                            "past": false
                        }
                    },
                    "raw_flags": 0
                }
            },
            "platform": {
                "base": "Raspberry Pi 4 Model B Rev 1.1", 
                "serial": "0000000000000000", 
                "type": "rpi"
            }
        },
        "meta": { 
            "kvm": {},
            "server": {
                "host": "localhost.localdomain"
            }
        },
        "system": {
            "kernel": {
                "machine": "x86_64",
                "release": "5.8.14-arch1-1",
                "system": "Linux",
                "version": "#1 SMP PREEMPT Wed, 07 Oct 2020 23:59:46 +0000"
            },
            "kvmd": {
                "version": "2.1"
            },
            "streamer": {
                "app": "ustreamer",
                "features": { 
                    "HAS_PDEATHSIG": true,
                    "WITH_GPIO": false,
                    "WITH_OMX": false,
                    "WITH_PTHREAD_NP": true,
                    "WITH_SETPROCTITLE": true
                },
                "version": "2.1"
            }
        }
    }
}"""
