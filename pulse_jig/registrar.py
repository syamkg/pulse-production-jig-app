class Registrar:
    def register_serial(self, serial):
        print(f"register_serial: {serial}")

    def submit_provisioning_record(self, hwspec, status, logs):
        print("submit_provisioning_record:")
        print(f"  status: {status}")
        print(f"  hwspec: {hwspec}")
        print(f"  logs: {logs[:70]}...")
