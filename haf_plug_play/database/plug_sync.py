import time
from threading import Thread

from haf_plug_play.database.access import WriteDb
from haf_plug_play.server.system_status import SystemStatus
from haf_plug_play.utils.tools import range_split
from haf_plug_play.plugs.polls.polls import WDIR_POLLS
from haf_plug_play.plugs.podping.podping import WDIR_PODPING

BATCH_PROCESS_SIZE = 200000
START_BLOCK_POLLS = 59594882
START_BLOCK_PODPING = 53691004 # TODO: confirm

class PlugInitSetup:

    db = WriteDb().db

    @classmethod
    def init(cls):
        for p in [WDIR_POLLS, WDIR_PODPING]:
            cls.setup_plug(p)
        cls.db.conn.close()

    @classmethod
    def setup_plug(cls, source_dir):
        tables = open(f'{source_dir}/tables.sql', 'r').read()
        functions = open(f'{source_dir}/functions.sql', 'r').read()
        cls.db.execute(tables, None)
        cls.db.execute(functions, None)
        cls.db.commit()


class PlugSync:

    # plug_name: state (None, loaded, syncing (10%), synced)
    plug_sync_states = {
        'polls': None,
        'podping': None
    }
    plug_sync_enabled = False
    
    @classmethod
    def sync_polls(cls):
        print('Starting plug sync: polls')
        db = WriteDb().db
        cls.plug_sync_states['polls'] = 'loaded'
        while True:
            if cls.plug_sync_enabled == True:
                head_hive_rowid = db.select("SELECT head_hive_opid FROM hpp.global_props;")
                assert head_hive_rowid is not None, "Null head_hive_opid found"
                if head_hive_rowid:
                    head_hive_rowid = head_hive_rowid[0][0] or 0
                else:
                    head_hive_rowid = 0
                _app_hive_rowid = db.select("SELECT latest_hive_opid FROM hpp.plug_sync WHERE plug_name = 'polls';")
                if _app_hive_rowid is None:
                    db.execute(
                        """INSERT INTO hpp.plug_sync (plug_name, latest_hive_opid)
                            VALUES ('polls',0);""", None)
                    db.commit()
                if not _app_hive_rowid:
                    # get start hive_rowid from start block
                    print("POLLS:: Finding app_hive_opid using start_block")
                    start_block = START_BLOCK_POLLS
                    while True:
                        _start_hive_rowid = db.select(f"SELECT min(id) FROM hive.plug_play_operations_view WHERE block_num = {start_block};")
                        if _start_hive_rowid:
                            app_hive_rowid = _start_hive_rowid[0][0]
                            print(f"POLLS:: Found {app_hive_rowid}")
                            break
                        start_block -= 1
                else:
                    app_hive_rowid = _app_hive_rowid[0][0]
                if (head_hive_rowid - app_hive_rowid) > 1000:
                    steps = range_split((app_hive_rowid + 1), head_hive_rowid, BATCH_PROCESS_SIZE)
                    for s in steps:
                        progress = round((s[1]/head_hive_rowid) * 100, 2)
                        cls.plug_sync_states['polls'] = f'synchronizing {progress} %'
                        SystemStatus.update_sync_status(plug_status=cls.plug_sync_states)
                        db.select(f"SELECT hpp.polls_update( {s[0]}, {s[1]} );")
                        db.commit()
                    cls.plug_sync_states['polls'] = 'synchronized'
                elif (head_hive_rowid - app_hive_rowid) > 0:
                    progress = round((app_hive_rowid/head_hive_rowid) * 100, 2)
                    cls.plug_sync_states['polls'] = f'synchronizing {progress} %'
                    db.select(f"SELECT hpp.polls_update( {app_hive_rowid+1}, {head_hive_rowid} );")
                    db.commit()
                    cls.plug_sync_states['polls'] = 'synchronized'
                else:
                    cls.plug_sync_states['polls'] = 'synchronized'
                SystemStatus.update_sync_status(plug_status=cls.plug_sync_states)
            time.sleep(0.2)
    
    @classmethod
    def sync_podping(cls):
        print('Starting plug sync: podping')
        db = WriteDb().db
        cls.plug_sync_states['podping'] = 'loaded'
        while True:
            if cls.plug_sync_enabled == True:
                head_hive_rowid = db.select("SELECT head_hive_opid FROM hpp.global_props;")
                assert head_hive_rowid is not None, "Null head_hive_opid found"
                if head_hive_rowid:
                    head_hive_rowid = head_hive_rowid[0][0] or 0
                else:
                    head_hive_rowid = 0
                _app_hive_rowid = db.select("SELECT latest_hive_opid FROM hpp.plug_sync WHERE plug_name = 'podping';")
                if _app_hive_rowid is None:
                    db.execute(
                        """INSERT INTO hpp.plug_sync (plug_name, latest_hive_opid)
                            VALUES ('podping',0);""", None)
                    db.commit()
                if not _app_hive_rowid:
                    # get start hive_rowid from start block
                    print("PODPING:: Finding app_hive_opid using start_block")
                    start_block = START_BLOCK_PODPING
                    while True:
                        _start_hive_rowid = db.select(f"SELECT min(id) FROM hive.plug_play_operations_view WHERE block_num = {start_block};")
                        if _start_hive_rowid:
                            app_hive_rowid = _start_hive_rowid[0][0]
                            print(f"PODPING:: Found {app_hive_rowid}")
                            break
                        start_block -= 1
                else:
                    app_hive_rowid = _app_hive_rowid[0][0]
                if (head_hive_rowid - app_hive_rowid) > 1000:
                    steps = range_split((app_hive_rowid + 1), head_hive_rowid, BATCH_PROCESS_SIZE)
                    for s in steps:
                        progress = round((s[1]/head_hive_rowid) * 100, 2)
                        cls.plug_sync_states['podping'] = f'synchronizing {progress} %'
                        SystemStatus.update_sync_status(plug_status=cls.plug_sync_states)
                        db.select(f"SELECT hpp.podping_update( {s[0]}, {s[1]} );")
                        db.commit()
                elif (head_hive_rowid - app_hive_rowid) > 0:
                    progress = round((app_hive_rowid/head_hive_rowid) * 100, 2)
                    cls.plug_sync_states['podping'] = f'synchronizing {progress} %'
                    db.select(f"SELECT hpp.podping_update( {app_hive_rowid+1}, {head_hive_rowid} );")
                    db.commit()
                else:
                    cls.plug_sync_states['podping'] = 'synchronized'
                SystemStatus.update_sync_status(plug_status=cls.plug_sync_states)
            time.sleep(0.2)
    
    @classmethod
    def toggle_plug_sync(cls, enabled=True):
        cls.plug_sync_enabled = enabled
    
    @classmethod
    def start_plugs(cls):
        # TODO: get enabled/disabled status for plugs from DB
        Thread(target=cls.sync_polls).start()
        Thread(target=cls.sync_podping).start()