import tarfile
import json

if __name__ == '__main__':
    with open('resources/configs/archiver.json', 'r') as f:
        config = json.load(f)

    with tarfile.open('resources/services.tar.gz', 'w:gz') as tar:
        tar.add(config['services'], arcname='')

    with tarfile.open('resources/checkers.tar.gz', 'w:gz') as tar:
        tar.add(config['checkers'], arcname='')
