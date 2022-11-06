# A10 CGNAT Repo

In this repo you can find below scripts:

- Get private IP from public IP (fixed-nat)

## Steps to run this Repo

- First you need to add your CGNAT devices on `config` file under scripts folder, below an example:

```
SHORT_ACTIVE_CGNAT_DEVICES_WITH_HOST = [
	["192.168.0.4", "CGNAT-HOST-NAME-1"],
	["192.168.0.8", "CGNAT-HOST-NAME-2"],
]
```

Then you need to add the the list of IPs in `cgnat_owner_ips.csv` under `files` folder as below:

```
IP Address,Port,Time,description
51.63.112.23,8307,14/05/2022 08:25:25,
51.63.112.23,8307,14/05/2022 09:25:25,
51.63.112.23,8307,14/05/2022 07:25:25,
51.63.112.23,8307,14/05/2022 09:25:25,
51.63.240.84,22197,14/05/2022 09:25:49,
51.63.32.187,,14/05/2022 09:25:34,
```

Then run below command to create virtual environment on root folder

```
python3 -m venv py_env
```

After that you need to activate the virtual environment

```
.\py_env\Scripts\activate
```

Then you need to install required python packages with below command:

```
pip install -r requirements.txt
```

Finally, now you are able to run the commands:

- To get the private IPs run below:

```
cd "scripts\CGN"
python.exe .\get_map_ip_with_thread.py
```
