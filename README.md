# AD-INFRA

Script for easy deployment of Attack-Defense CTFs.

## Usage

1. Create `config.yaml` and `teams.yaml` configuration files and fill them with data. Examples can be found [here for config.yaml](/config.example.yaml) and [here for example.yaml](/teams.example.yaml), also there is a [configuration reference on the wiki](https://github.com/LeKSuS-04/ad-infra/wiki/Configuration).
2. Run `make docker-build` or `make docker-pull` to prepare Docker image;
3. Use container to manage your infrastructure;
4. Run `make docker-clean` to clean your system from used volumes and images.

## Make recipes

### Infrastructure

- `plan` - calculates amount of resources required for deployment of infrastructure with specified configuration;
- `deploy` - deploys and configures infrastructure;
- `destroy` - destroys infrastructure.

### Docker helpers

- `docker-build` - builds image from the sources;
- `docker-pull` - pulls pre-built image from the Docker Hub;
- `docker-clean` - removes the image and all the volumes for system, as if the container have never existed.

## More information

You can read more about structure and ideas of this script on the [wiki page](https://github.com/LeKSuS-04/ad-infra/wiki).

---

Made by [LeKSuS](https://github.com/LeKSuS-04), distributed under the [GNU General Public License v3](https://www.gnu.org/licenses/gpl-3.0.html).
