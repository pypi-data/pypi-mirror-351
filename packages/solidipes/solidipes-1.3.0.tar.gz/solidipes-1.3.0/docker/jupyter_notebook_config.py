# Configuration file for jupyter-notebook.
import os

fb_config_dir = "/home/jovyan/.filebrowser"
fb_config = os.path.join(fb_config_dir, "filebrowser.db")
baseurl = open("/tmp/baseurl").read().strip()


try:
    os.mkdir(fb_config_dir)
except FileExistsError:
    pass


os.system(f"cp /tmp/filebrowser.db {fb_config}")
os.system(f"filebrowser --database={fb_config} config set -b {baseurl}")

c.ServerProxy.servers = {  # noqa: F821
    "solidipes": {
        "command": [
            "solidipes",
            "report",
            "web_report",
            "./",
            "--theme.base",
            "light",
            "--server.port",
            "8501",
            "--browser.serverAddress",
            "0.0.0.0",
        ],
        "port": 8501,
        "timeout": 60,
    },
    "server": {"command": ["streamlit-pyvista", "run", "proxy"], "port": 5000, "timeout": 60},
    "filebrowser": {
        "command": [
            "filebrowser",
            "--noauth",
            "--port=8502",
            "--root=./",
            "--disable-exec",
            f"--database={fb_config}",
            f"--baseurl={baseurl}",
        ],
        "port": 8502,
        "timeout": 60,
    },
}
