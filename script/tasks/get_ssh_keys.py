import os
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


from tools import task, Syncer, Resource, log
from constants.paths import GENERATED_PATH


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


def _load_existing_ssh_key(sync: Syncer, priv_key_path: Path):
    sync.set_resource(Resource.ADMIN_SSH_KEY_FILE, priv_key_path)
    log("Found existing SSH key")

    key = _load_private(priv_key_path)
    sync.set_resource(Resource.ADMIN_SSH_KEY, key)
    log("SSH key loaded")


def _generate_new_ssh_key(sync: Syncer, pub_key_path: Path, priv_key_path: Path):
    log("Generating SSH key")
    key = ec.generate_private_key(ec.SECP256R1())
    sync.set_resource(Resource.ADMIN_SSH_KEY, key)
    log("SSH key generated")

    _save_private(key, priv_key_path)
    _save_public(key, pub_key_path)
    log("SSH key saved")
    sync.set_resource(Resource.ADMIN_SSH_KEY_FILE, priv_key_path)


@task(depends_on=[])
def get_ssh_keys(sync: Syncer):
    ssh_key_file = "id_ecdsa"
    priv_key_path = GENERATED_PATH / ssh_key_file
    pub_key_path = GENERATED_PATH / f"{ssh_key_file}.pub"

    if priv_key_path.exists() or pub_key_path.exists():
        _load_existing_ssh_key(sync, priv_key_path)
    else:
        _generate_new_ssh_key(sync, pub_key_path, priv_key_path)
