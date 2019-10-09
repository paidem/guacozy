ProtocolsDict = {
    "rdp": {"name": "RDP",
            "description": "Remote Desktop Protocol",
            "port": 3389,
            },
    "vnc": {"name": "VNC",
            "description": "VNC Protocol",
            "port": 5901,
            },
    "ssh": {"name": "SSH",
            "description": "Secure SHell",
            "port": 22,
            },
    "telnet": {"name": "Telnet",
               "description": "Telnet",
               "port": 21,
               }
}

RDPSecurityDict = {
    "rdp": {"name": "RDP",
            "description": "Standard RDP encryption",
            },
    "nla": {"name": "NLA",
            "description": "Network Level Authentication. "
                           "This mode requires the username and password, "
                           "and performs an authentication step before the "
                           "remote desktop session actually starts. "
                           "If the username and password are not given, "
                           "the connection cannot be made.",
            },
    "tls": {"name": "TLS",
            "description": "Transport Layer Security",
            },
    "any": {"name": "ANY",
            "description": "Allow the server to choose the type of security.",
            }
}
