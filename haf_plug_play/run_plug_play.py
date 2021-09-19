import os
from threading import Thread


from haf_plug_play.config import Config
from haf_plug_play.server.serve import run_server
from haf_plug_play.server.system_status import SystemStatus

config = Config.config



def run():
    print("---   Hive Plug & Play (HAF)started   ---")
    # TODO: link with HAF sync status
    SystemStatus.set_sync_status(2999999,"2016-07-07 21:24:54", False)
    run_server(config)


if __name__ == "__main__":
    run()