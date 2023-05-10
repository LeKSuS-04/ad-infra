import os
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec

from synchronization import Synchronizator, Resource


@Synchronizator.task(depends_on=[])
def generate_ssh_keys(sync: Synchronizator):
    key = ec.generate_private_key(
        ec.SECP256K1()
    )
    sync.set_resource(Resource.ADMIN_SSH_KEY, key)

    generated_path = Path.cwd() / 'generated'
    priv_key_path = generated_path / 'id_ecdsa'
    pub_key_path = generated_path / 'id_ecdsa.pub'
    with open(priv_key_path, 'wb') as priv, open(pub_key_path, 'wb') as pub:
        priv.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.OpenSSH,
            encryption_algorithm=serialization.NoEncryption()
        ))
        pub.write(key.public_key().public_bytes(
            serialization.Encoding.OpenSSH,
            serialization.PublicFormat.OpenSSH
        ))

    os.chmod(priv_key_path, 0o600)