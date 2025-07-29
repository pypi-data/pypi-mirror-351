import logging
log = logging.getLogger(__name__)

try:
    import appdirs
    from pathlib import Path
    import json
except ModuleNotFoundError as err:
    # Error handling
    log.error(err)
    raise


class Pms800Conf():
    default_path = f"{appdirs.user_data_dir(appauthor='BH',appname='bhpy')}/Pms800/Config.json"
    pass


class SpcQcX08Conf():
    default_path = f"{appdirs.user_data_dir(appauthor='BH',appname='bhpy')}/SpcQcX08/Config.json"
    pass


class SpcQcX04Conf():
    default_path = f"{appdirs.user_data_dir(appauthor='BH',appname='bhpy')}/SpcQcX04/Config.json"

    POSITIVE_EDGE = "͟  |͞   (rising)"
    NEGATIVE_EDGE = "͞  |͟   (falling)"

    POS_NEG_LIST = [POSITIVE_EDGE, NEGATIVE_EDGE]

    DELTA_TIME_MODE = "Δt"

    def __init__(self, config_path: str = default_path) -> None:
        SpcQcX04Conf.default_path = config_path
        self.selectedCard = '1'
        self.restore_defaults()
        self.load_conf(config_path)

    def load_conf(self, conf_path=None) -> None:
        if conf_path is None:
            conf_path = self.default_path
        try:
            with open(conf_path, 'r', encoding='utf8') as f:
                json_conf = json.load(f)
                for name in json_conf:
                    setattr(self, name, json_conf[name])
        except FileNotFoundError:
            self.write_conf(conf_path)

    def write_conf(self, conf_path=None) -> None:
        if conf_path is None:
            conf_path = self.default_path
        conf_dict = self.__dict__
        conf_dict.pop('default_path', None)
        Path(conf_path).parent.mkdir(parents=True, exist_ok=True)
        with open(conf_path, 'w', encoding='utf8') as f:
            json.dump(conf_dict, f, indent=2, sort_keys=True, default=str, ensure_ascii=False)

    def restore_config(self) -> None:
        '''Resets the Hardware settings.

        Settings that require little or no changes after initial setup
        because they are tied to the measurement system's components and
        their assembly, get set to values that are either the hardware
        defaults or good starting point'''
        # Channel wise settings
        self.threshold = [-50.0, -50.0, -50.0, -50.0]
        self.zeroCross = [12.0, 12.0, 12.0, 12.0]
        self.syncEn = [False, False, False, True]
        self.syncDiv = [1, 1, 1, 1]
        self.routingEn = [True, True, True, False]
        self.routingDelay = 0.0

        # Marker wise settings
        self.markerEn = [False, False, False, False]
        self.markerEdge = [self.POSITIVE_EDGE, self.POSITIVE_EDGE, self.POSITIVE_EDGE,
                           self.POSITIVE_EDGE]

        # Other settings
        self.ditheringEn = True
        self.externalTrigEn = False
        self.triggerEdge = self.POSITIVE_EDGE

    def restore_measurement(self) -> None:
        '''Resets the measurement parameters

        Parameters that are related to the individual measurement, that
        may be changed according to the need of the test specimen or the
        expected/desired experiment results'''
        self.channelDelay = [0., 0., 0., 0.]
        self.timeRangePs = 4_194_573
        self.frontClippingNs = 0
        self.measuringDurationNs = 0
        self.stopOnTime = False
        self.dllAutoStopTimeNs = 0
        self.mode = self.DELTA_TIME_MODE
        self.resolution = 12

    def restore_defaults(self) -> None:
        '''Resets all settings and parameters

        Dispatcher call for all different categories of settings and
        parameters'''
        self.restore_config()
        self.restore_measurement()
