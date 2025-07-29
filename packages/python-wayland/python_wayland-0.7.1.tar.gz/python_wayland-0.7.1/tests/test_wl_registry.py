import wayland as wl
from tests.utils import process_messages

wayland = wl.initialise()


def test_get_registry():
    protocols = ["wl_shm", "xdg_wm_base", "wl_compositor"]

    received_protocols = []

    def on_wl_registry_global(name, interface, version):
        nonlocal received_protocols
        received_protocols.append(interface)

    # Hook the event to get the registry results
    wayland.wl_registry.events.global_ += on_wl_registry_global
    wayland.wl_display.get_registry()
    process_messages(wayland)

    # Check we got some interfaces we should have
    for proto in protocols:
        assert proto in received_protocols
