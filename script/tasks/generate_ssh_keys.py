import os
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


from tools import task, Syncer, Resource, log
from constants.paths import GENERATED_PATH


def _save_private(key: ec.EllipticCurvePrivateKey, path: Path):
    if path.exists():
        log("Private key file found, skipping generation")
        return

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
    if path.exists():
        log("Public key file found, skipping generation")
        return

    with open(path, "wb") as pub:
        pub.write(
            key.public_key().public_bytes(
                serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH
            )
        )


@task(depends_on=[])
def generate_ssh_keys(sync: Syncer):
    key = ec.generate_private_key(ec.SECP256R1())
    sync.set_resource(Resource.ADMIN_SSH_KEY, key)

    ssh_key_file = "id_ecdsa"
    _save_private(key, GENERATED_PATH / ssh_key_file)
    _save_public(key, GENERATED_PATH / f"{ssh_key_file}.pub")

    sync.set_resource(Resource.ADMIN_SSH_KEY_FILE, ssh_key_file)
