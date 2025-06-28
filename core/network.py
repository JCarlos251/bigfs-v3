# Interface Pyro5 para registro e localização

from Pyro5.api import locate_ns, Daemon

from core.constants import NAMESERVER_HOST, NAMESERVER_PORT

def get_nameserver():
    return locate_ns(host=NAMESERVER_HOST, port=NAMESERVER_PORT)

def start_daemon():
    return Daemon(host="localhost")  # localhost, você pode trocar

def register_service(name, obj, daemon):
    ns = get_nameserver()
    uri = daemon.register(obj)
    ns.register(name, uri)
    return uri