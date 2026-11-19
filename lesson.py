from netmiko import ConnectHandler

router_device = {
    'device_type': 'cisco_ios_telnet',
    'host': '192.168.10.104',  # 'host' is preferred, though 'ip' also works
    'port': 32770,
    'username': 'admin',
    'password': 'eve',
    'secret': 'eve',
    'fast_cli': False,         # Helps prevent timeout issues on Cisco devices
}

try:
    print("Connecting to the router...")

    net_connect = ConnectHandler(**router_device)
    net_connect.enable()

    # Disable paging so the router doesn't pause at "--More--"
    net_connect.send_command("terminal length 0")

    commands_to_run = [
        "show version",
        "show ip interface brief",
        "show running-config"
    ]

    for cmd in commands_to_run:
        print(f"\n--- Output for: {cmd} ---")

        # Fix: Use the 'cmd' variable, not a hardcoded string. 
        # Fix: Use r"#" for the expect_string.
        output = net_connect.send_command(
            command_string=cmd,
            read_timeout=120,
            expect_string=r"#"
        )

        print(output)

    net_connect.disconnect()
    print("\nDisconnected successfully.")

except Exception as e:
    print(f"Connection failed: {e}")