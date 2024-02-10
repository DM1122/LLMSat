"""Remote sensing manager class."""


from cmd2 import CommandSet, with_default_category


@with_default_category("RemoteSensingManager")
class RemoteSensingManager(CommandSet):
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RemoteSensingManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, krpc_connection=None):
        """Experiment manager class."""
        if RemoteSensingManager._initialized:
            return
        super().__init__()

        self.connection = krpc_connection
        self.vessel = self.connection.space_center.active_vessel

        RemoteSensingManager._initialized = True

    @staticmethod
    def _get_cmd_instance():
        """Gets the cmd for use by argument parsers for poutput."""
        return RemoteSensingManager()._cmd

    def do_get_parts(self, statement):
        output = self.get_module()
        self._cmd.poutput(output)

    def get_module(self):
        # HECS2.ProbeCore', 'scansat-multi-msi-1', 'RelayAntenna100', 'batteryBank', 'batteryBank', 'advSasModule', 'scansat-recon-ikonos-1', 'scansat-recon-worldview-3-1', 'largeSolarPanel', 'largeSolarPanel', 'scansat-resources-hyperion-1']
        part = self.vessel.parts.with_name("scansat-multi-msi-1")[0]  # assumes only one
        modules = [x.name for x in part.modules]
        module = part.modules[4]
        module_dict = module.events

        return module_dict
