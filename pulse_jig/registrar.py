class Registrar:
    def register_serial(self, serial: str):
        print(f"register_serial: {serial}")

    def submit_provisioning_record(self, hwspec: dict, status: str, logs: str):
        print("submit_provisioning_record:")
        print(f"  status: {status}")
        print(f"  hwspec: {hwspec}")
        print(f"  logs: {logs[:70]}...")
