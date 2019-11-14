from blinker import Namespace

bip_signals = Namespace()


reload_menu_tree = bip_signals.signal('reload-menu-tree')
