import logging

from .probe_provisioner import ProbeProvisioner
from lib.target import Target

from pulse_jig.config import settings

logger = logging.getLogger("provisioner")


class ProbeProvisionerTa11k(ProbeProvisioner):
    def __init__(self, registrar, pulse_manager, dev):
        super().__init__(registrar, pulse_manager, dev)
        self.mode.target = Target.TA11K

    def running_tests(self):
        passed = self._ftf.test_ta11k(self._port_no, settings.app.test_port_min_threshold)

        if passed:
            logger.info("Tests Passed!")
            self.set_status_passed()
            self.proceed()
        else:
            logger.error("Tests Failed!")
            self.fail()
