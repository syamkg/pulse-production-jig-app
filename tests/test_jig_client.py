from pulse_jig.jig_client import JigClient, JigClientException
import serial
import pytest


@pytest.fixture
def port():
    return serial.serial_for_url("loop://")


def test_send_command_returns_the_body_on_success(port):
    port.write(b"SELF_TEST\r\n")
    port.write(b"+OK\r\n")
    port.write(b"testing watchdog...OK\r\n")
    port.write(b"testing EEPROM...OK\r\n")
    port.write(b".\r\n")
    client = JigClient(port)
    assert client.send_command("SELF_TEST") == "\n".join(["testing watchdog...OK", "testing EEPROM...OK"])


def test_send_command_works_when_prompt_present(port):
    port.write(b"> SELF_TEST\r\n")
    port.write(b"+OK\r\n")
    port.write(b"testing EEPROM...OK\r\n")
    port.write(b".\r\n")
    client = JigClient(port)
    assert client.send_command("SELF_TEST") == "testing EEPROM...OK"


def test_send_command_raises_exception_on_error_response(port):
    port.write(b"SELF_TEST\r\n")
    port.write(b"-ERR\r\n")
    client = JigClient(port)
    with pytest.raises(JigClient.CommandFailed):
        assert client.send_command("SELF_TEST")


def test_send_command_throws_error_on_acknowledgement_timeout(port):
    port.write(b"SELF_TEST\r\n")
    client = JigClient(port)
    with pytest.raises(JigClientException):
        assert client.send_command("SELF_TEST")


def test_run_returns_error_on_body_timeout(port):
    port.write(b"SELF_TEST\r\n")
    port.write(b"+OK\r\n")
    port.write(b"some body\r\n")
    client = JigClient(port)
    with pytest.raises(JigClientException):
        client.send_command("SELF_TEST")


def test_run_test_cmd_detects_pass(port):
    port.write(b"> SELF_TEST\r\n")
    port.write(b"+OK\r\n")
    port.write(b"PASS\r\n")
    port.write(b".\r\n")
    client = JigClient(port)
    assert client.run_test_cmd("SELF_TEST") is True


def test_run_test_cmd_detects_failure(port):
    port.write(b"> SELF_TEST\r\n")
    port.write(b"+OK\r\n")
    port.write(b"FAIL\r\n")
    port.write(b".\r\n")
    client = JigClient(port)
    assert client.run_test_cmd("SELF_TEST") is False


def test_run_test_cmd_fails_on_no_status(port):
    port.write(b"> SELF_TEST\r\n")
    port.write(b"+OK\r\n")
    port.write(b"some log...\r\n")
    port.write(b".\r\n")
    client = JigClient(port)
    assert client.run_test_cmd("SELF_TEST") is False
