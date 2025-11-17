# Web Dashboard
A remote dashboard that runs the startup script on the cyberdeck and displays sensor data 

> startup script is different from main as it does not log data and sends JSON data to the dashboard

Using a **ThinkCentre M700** running **[Proxmox VE](https://www.proxmox.com/en/)**. An **LXC container** running **Ubuntu 25.04 with 2GB memory and 1GB swap**

![dashboard](../demos/web_dashboard_demo.gif)

### Resources
* **[Svelte and Flask Dashboard Tutorial](https://testdriven.io/blog/flask-svelte/)**
* **[Paramiko Python SSH Tutorial](https://www.devdungeon.com/content/python-ssh-tutorial#toc-3)**

### Software
* **[Proxmox](https://www.proxmox.com/en/)**
* **[Test Script](./test.py)**
* **[Frontend](./frontend)**
* **[Backend](./backend)**

#### Frontend
* **[Svelte](https://svelte.dev/)**
* **SvelteKit**

#### Backend
* **[Flask](https://flask.palletsprojects.com/en/stable/)**
* **JSON**
* **[Paramiko](https://www.paramiko.org/)**

### Hardware
* **Lenovo ThinkCentre M700**

### Diagrams

#### Proxmox Web Directory
![web to cybedeck](../images/diagrams/web_to_dashboard_diagram.jpg)

#### How Proxmox Interacts With The Cyberdeck
![dashboard](../images/diagrams/dashboard_diagram.jpg)



### Startup
```
cd web_dashboard/
npm install
npm run dev  
```
