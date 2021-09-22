from pulse_jig.jig_client import JigClient, JigClientException
import serial
import pytest


@pytest.fixture
def client():
    port = serial.serial_for_url("loop://")
    return JigClient(port)


def test_send_command_returns_the_body_on_success(client):
    client.port.write(b"SELF_TEST\r\n")
    client.port.write(b"+OK\r\n")
    client.port.write(b"testing watchdog...OK\r\n")
    client.port.write(b"testing EEPROM...OK\r\n")
    client.port.write(b".\r\n")
    assert client.send_command("SELF_TEST") == "\n".join(
        ["testing watchdog...OK", "testing EEPROM...OK"]
    )


def test_send_command_works_when_prompt_present(client):
    client.port.write(b"> SELF_TEST\r\n")
    client.port.write(b"+OK\r\n")
    client.port.write(b"testing EEPROM...OK\r\n")
    client.port.write(b".\r\n")
    assert client.send_command("SELF_TEST") == "testing EEPROM...OK"


def test_send_command_return_false_on_negative_ack(client):
    client.port.write(b"SELF_TEST\r\n")
    client.port.write(b"-ERR\r\n")
    with pytest.raises(JigClientException):
        assert client.send_command("SELF_TEST")


def test_send_command_throws_error_on_acknowledgement_timeout(client):
    client.port.write(b"SELF_TEST\r\n")
    with pytest.raises(JigClientException):
        assert client.send_command("SELF_TEST")


def test_run_returns_error_on_body_timeout(client):
    with pytest.raises(JigClientException):
        client.port.write(b"SELF_TEST\r\n")
        client.port.write(b"+OK\r\n")
        client.port.write(b"some body\r\n")
        client.send_command("SELF_TEST")
