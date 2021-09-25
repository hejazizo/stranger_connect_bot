from types import SimpleNamespace

from utils import create_keyboard


keys = SimpleNamespace(**dict(
    random_connect=':bust_in_silhouette: Random Connect',
    settings=':gear: Settings',
    back=':cross_mark: Back',
    disconnect=':cross_mark: Disconnect'
))

keyboards = SimpleNamespace(**dict(
    main=create_keyboard([keys.random_connect, keys.settings]),
    back=create_keyboard([keys.back]),
    talking=create_keyboard([keys.disconnect])
))

states = SimpleNamespace(**dict(
    init='Initialized Bot',
    random_connect='Waiting for Random Connection',
    settings='Settings Menu',
    talking='Talking to Stranger'
))
