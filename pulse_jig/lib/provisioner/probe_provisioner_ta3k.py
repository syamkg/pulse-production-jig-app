import logging

from .probe_provisioner import ProbeProvisioner
from lib.target import Target

logger = logging.getLogger("provisioner")


class ProbeProvisionerTa3k(ProbeProvisioner):
    def __init__(self, registrar, pulse_manager, dev):
        super().__init__(registrar, pulse_manager, dev)
        self.mode.target = Target.TA3K

    def running_tests(self):
        passed = self._ftf.test_ta3k(self._port_no)

        if passed:
            logger.info("Tests Passed!")
            self.set_status_passed()
            self.proceed()
        else:
            logger.error("Tests Failed!")
            self.fail()
