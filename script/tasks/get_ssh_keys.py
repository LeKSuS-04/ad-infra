import os
from pathlib import Path

from constants.paths import PRIV_SSH_KEY_FILE_PATH, PUB_SSH_KEY_FILE_PATH
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from tools import Resource, Syncer, log, task


def _save_private(key: ec.EllipticCurvePrivateKey, path: Path):
    with open(path, "wb") as priv:
        priv.write(
            key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.OpenSSH,
                encryption_algorithm=serialization.NoEncryption(),
            )
        )
    os.chmod(path, 0o600)


def _save_public(key: ec.EllipticCurvePrivateKey, path: Path):
    with open(path, "wb") as pub:
        pub.write(
            key.public_key().public_bytes(
                serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH
            )
        )


def _load_private(path: Path) -> ec.EllipticCurvePrivateKey:
    with open(path, "rb") as priv:
        data = priv.read()
        key = serialization.load_ssh_private_key(data, password=None)
        assert isinstance(
            key, ec.EllipticCurvePrivateKey
        ), f'Bad private key format: expected "EllipticCurvePrivateKey", got "{type(key).__name__}"'
        return key


def _load_existing_ssh_key(sync: Syncer):
    sync.set_resource(Resource.ADMIN_SSH_KEY_FILE_SAVED)
    log("Found existing SSH key")

    key = _load_private(PRIV_SSH_KEY_FILE_PATH)
    sync.set_resource(Resource.ADMIN_SSH_KEY, key)
    log("SSH key loaded")


def _generate_new_ssh_key(sync: Syncer):
    log("Generating SSH key")
    key = ec.generate_private_key(ec.SECP256R1())
    sync.set_resource(Resource.ADMIN_SSH_KEY, key)
    log("SSH key generated")

    _save_private(key, PRIV_SSH_KEY_FILE_PATH)
    _save_public(key, PUB_SSH_KEY_FILE_PATH)
    log("SSH key saved")
    sync.set_resource(Resource.ADMIN_SSH_KEY_FILE_SAVED)


@task(depends_on=[])
def get_ssh_keys(sync: Syncer):
    if PRIV_SSH_KEY_FILE_PATH.exists() and PUB_SSH_KEY_FILE_PATH.exists():
        _load_existing_ssh_key(sync)
    else:
        _generate_new_ssh_key(sync)
