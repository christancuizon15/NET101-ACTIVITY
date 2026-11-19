from flask import Flask, request
from netmiko import ConnectHandler

app = Flask(__name__)

router_device = {
    'device_type': 'cisco_ios_telnet',
    'host': '192.168.10.104',
    'port': 32770,
    'username': 'admin',
    'password': 'eve',
    'secret': 'eve',
    'fast_cli': False,
}

# --- HTML TEMPLATE WITH CSS ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Router Dashboard</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-main: #e2e8f0;
            --text-muted: #94a3b8;
            --accent: #38bdf8;
            --success: #10b981;
            --error: #ef4444;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #334155;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        h1 {
            margin: 0;
            color: var(--accent);
            font-size: 24px;
        }
        .status-badge {
            background-color: var(--success);
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: bold;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .status-badge::before {
            content: '';
            display: block;
            width: 8px;
            height: 8px;
            background-color: white;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(255, 255, 255, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(255, 255, 255, 0); }
        }
        .card {
            background-color: var(--card-bg);
            border-radius: 8px;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            border: 1px solid #334155;
        }
        .card-header {
            background-color: #0f172a;
            padding: 15px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #334155;
        }
        .card-header h2 {
            margin: 0;
            font-size: 16px;
            color: var(--accent);
            font-family: monospace;
        }
        .copy-btn {
            background-color: transparent;
            color: var(--text-muted);
            border: 1px solid var(--text-muted);
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s;
        }
        .copy-btn:hover {
            background-color: var(--text-muted);
            color: var(--bg-color);
        }
        pre {
            margin: 0;
            padding: 20px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.5;
            overflow-x: auto;
            color: #a78bfa;
        }
        .error {
            border-color: var(--error);
        }
        .error h1 {
            color: var(--error);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🖧 Network Automation Dashboard</h1>
            <div class="status-badge">LIVE</div>
        </div>
        {content}
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def get_router_info():
    try:
        print("Connecting to the router...")
        
        net_connect = ConnectHandler(**router_device)
        net_connect.enable()
        net_connect.send_command("terminal length 0")
        
        commands_to_run = [
            "show version",
            "show ip interface brief",
            "show running-config"
        ]
        
        results = {}
        
        for cmd in commands_to_run:
            output = net_connect.send_command(
                command_string=cmd,
                read_timeout=120,
                expect_string=r"#"
            )
            results[cmd] = output
            
        net_connect.disconnect()
        print("Disconnected successfully.")
        
        # Build the HTML content dynamically for each command
        html_content = ""
        for cmd, output in results.items():
            html_content += f"""
            <div class="card">
                <div class="card-header">
                    <h2>{cmd}</h2>
                    <button class="copy-btn" onclick="copyText('{cmd}')">Copy</button>
                </div>
                <pre id="{cmd}">{output}</pre>
            </div>
            """
        
        # Insert the generated cards into the main template
        final_html = HTML_TEMPLATE.replace("{content}", html_content)
        
        # Add a simple JavaScript function for the Copy button
        final_html = final_html.replace("</body>", """
        <script>
            function copyText(elementId) {
                const text = document.getElementById(elementId).innerText;
                navigator.clipboard.writeText(text).then(() => {
                    alert('Output copied to clipboard!');
                });
            }
        </script>
        </body>""")
        
        return final_html
        
    except Exception as e:
        error_html = f"""
        <div class="card error">
            <div class="card-header">
                <h2>Error</h2>
            </div>
            <pre>Connection Failed: {str(e)}</pre>
        </div>
        """
        final_error = HTML_TEMPLATE.replace("{content}", error_html)
        return final_error, 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)