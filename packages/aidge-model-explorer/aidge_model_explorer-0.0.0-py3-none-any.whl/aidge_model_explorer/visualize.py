import threading
import time
import requests
import socket
import sys
import portpicker
import aidge_core
from model_explorer import visualize_from_config
from IPython.display import IFrame, display
from IPython import get_ipython
from .config import config
from .consts import (
    DEFAULT_PORT,
    DEFAULT_HOST,
)


def _is_port_in_use(host: str, port: int) -> bool:
  try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
      return s.connect_ex((host, port)) == 0
  except socket.gaierror:
    print(
        f'"{host}" cannot be resolved. Try using IP address directly:'
        ' model-explorer --host=127.0.0.1'
    )
    sys.exit(1)

def visualize(graphview, name, host=DEFAULT_HOST, port=DEFAULT_PORT, no_open_in_browser=False) -> None:
    if get_ipython():
        show_IFrame(
            graphview,
            name,
            host=host,
            port=port
        )
    else:
        show_server(
            graphview,
            name,
            host=host,
            port=port,
            no_open_in_browser=no_open_in_browser
        )

def show_server(graphview, name, host=DEFAULT_HOST, port=DEFAULT_PORT, no_open_in_browser=False) -> None:
    conf = config()
    conf.add_graphview(graphview, name)
    visualize_from_config(
        config = conf,
        host= host,
        port=port,
        no_open_in_browser=no_open_in_browser
    )

def show_IFrame(graphview, name, host=DEFAULT_HOST, port=DEFAULT_PORT) -> None:
    if get_ipython() is None:
        raise RuntimeError("This function should only be used inside of a Notebook.")
    conf = config()
    conf.add_graphview(graphview, name)


    if _is_port_in_use(host, port):
        aidge_core.Log.notice(f"{host}::{port} is already taken, finding another port")
        found_port = False
        for i in range(0, 20):
            port = port + i
            if not _is_port_in_use(host, port):
                found_port = True
                break
        if not found_port:
            port = portpicker.pick_unused_port()
        aidge_core.Log.notice(f"New port used: {host}::{port}")

    app_thread = threading.Thread(target=lambda: visualize_from_config(
        config = conf,
        host= host,
        port=port,
        no_open_in_browser=True
    ))

    app_thread.daemon = True
    aidge_core.Log.debug("Starting server ...")
    app_thread.start()
    starting_time = time.time()
    while True:
        try:
            response = requests.get(f'http://{host}:{port}/')
        except:
            continue

        if response.status_code == 200:
            aidge_core.Log.debug("Server found!")
            break
        elif time.time() - starting_time > 10:
            raise RuntimeError(f"Trying to detect app for 10s failed, http error {response.status_code}")
    url = f"http://{host}:{port}/?data={conf.to_url_param_value()}"
    aidge_core.Log.debug(f"Opening IFrame {url}")
    display(IFrame(src=url, width="100%", height="600"))