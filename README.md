# AD-INFRA

Script for easy deployment of Attack-Defense CTFs.

> [!WARNING]
> I don't remember what's current state of this repository is. Some stuff could be suboptimal, there might be flaws and drawbacks and straight up bugs. I don't care anymore. I still believe that my work can be important as a reference for those who care about CTFs, so I am publishing it despite it's messy state. Use with caution (or better yet, just look, learn, question everything and implement your infra yourself)
>
> Also see `dev` branch, I think I've left some useful stuff there, although in even messier state than `master`

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

### Other

- `shell` - drops you into the shell inside the container. Useful for inspecting volumes and debugging stuff in same environment in which everything is executed.

## More information

You can read more about structure and ideas of this script on the [wiki page](https://github.com/LeKSuS-04/ad-infra/wiki).

---

Made by [LeKSuS](https://github.com/LeKSuS-04), distributed under the [GNU General Public License v3](https://www.gnu.org/licenses/gpl-3.0.html).
