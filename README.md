# HONEYPY

A modular, graphic-based honeypot to capture IP Adresses, usernames, passwords, and commands from various protocols (SSH & HTTP supported right now). Written in Python.

# Install

**1) Clone repository.**
`git clone https://github.com/sutharshan-xyz/Honeypot.git`

**2) Permissions.**
Move into `Honeypot` folder.

Ensure `main.py` has proper permisions. (`chmod 755 honeypy.py`)

**3) Keygen.**

An RSA key must be generated for the SSH server host key. The SSH host key provides proper identification for the SSH server. Ensure the key is titled `server.key` and resides in the same relative directory to the main program.

`ssh-keygen -t rsa -b 2048 -f server.key`

# Usage

To provision a new instance of HONEYPY, use the `honeypy.py` file. This is the main file to interface with for HONEYPY. 

HONEYPY requires a bind IP address (`-a`) and network port to listen on (`-p`). Use `0.0.0.0` to listen on all network interfaces. The protocol type must also be defined.

```
-a / --address: Bind address.
-p / --port: Port.
-s / --ssh OR -wh / --http: Declare honeypot type.
```

Example: `python3 honeypy.py -a 0.0.0.0 -p 22 --ssh`

💡 If HONEPY is set up to listen on a privileged port (22), the program must be run with `sudo` or root privileges. No other services should be using the specified port. 

If port 22 is being used as the listener, the default SSH port must be changed.

❗ To run with `sudo`, the `root` account must have access to all Python libraries used in this project (libraries defined in `requirements.txt`). Install by switching to the root account, then supply:

`root@my_host# pip install -r requirements`

This will install all the packages for the root user, but it will affect the global environment and isn't considered the "safeest" way to do this.

**Optional Arguments**

A username (`-u`) and password (`-w`) can be specified to authenticate the SSH server. The default configuration will accept all usernames and passwords.

```
-u / --username: Username.
-w / --password: Password.
-t / --tarpit: For SSH-based honeypots, -t can be used to trap sessions inside the shell, by sending a 'endless' SSH banner.
```

Example: `python3 main.py -a 0.0.0.0 -p 22 --ssh -u admin -w admin --tarpit`

# Logging Files

HONEYPY has three loggers configured. Loggers will route to either `cmd_audits.log`, `creds_audits.log` (for SSH), and `http_audit.log` (for HTTP) log files for information capture.

`cmd_audits.log`: Captures IP address, username, password, and all commands supplied.

`creds_audits.log`: Captures IP address, username, and password, comma seperated. Used to see how many hosts attempt to connect to SSH_HONEYPY.

`http_audit.log`: Captures IP address, username, password.


# Honeypot Types
This honeypot was written with modularity in mind to support future honeypot types (Telnet, HTTPS, SMTP, etc). As of right now there are two honeypot types supported.

## SSH
The project started out with only supported SSH. Use the following instructions above to provision an SSH-based honeypot which emulates a basic shell.

💡 `-t / --tarpit`: A tarpit is a security mechanism designed to slow down or delay the attempts of an attacker trying to brute-force login credentials. Leveraging Python's time module, a very long SSH-banner is sent to a connecting shell session. The only way to get out of the session is by closing the terminal. 

## HTTP
Using Python Flask as a basic template to provision a simple web service, HONEYPY impersonates a default WordPress `wp-admin` login page. Username / password pairs are collected.

There are default credentials accepted, `admin` and `deeboodah`, which will proceed to a Rick Roll gif. Username and password can be changed using the `-u / --username: Username.
-w / --password: Password` arguments.

The web-based honeypot runs on port 5000 by default. This can be changed using the `-p / --port` flag option.
