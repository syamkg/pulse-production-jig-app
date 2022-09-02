import logging

from .probe_provisioner import ProbeProvisioner

logger = logging.getLogger("provisioner")


class ProbeProvisionerTa11k(ProbeProvisioner):
    def running_tests(self):
        passed = self._ftf.test_ta11k(self._port_no)

        if passed:
            logger.info("Tests Passed!")
            self.set_status_passed()
            self.proceed()
        else:
            logger.error("Tests Failed!")
            self.fail()