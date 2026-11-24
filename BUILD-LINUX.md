# Linux releases

The `Linux release` workflow builds and tests statically linked amd64 and arm64
packages on native GitHub-hosted runners. No Docker Hub credentials are needed.
Push a `v*` tag to publish both archives and SHA-256 files in one GitHub Release;
publication happens only after both builds and conversion smoke tests succeed.

Local build (Docker required):

```sh
docker build -f scripts/Dockerfile.release --output type=local,dest=release .
tar -C release -czf subconverter_linux64.tar.gz subconverter
```

Choose the archive name for the architecture you actually built. To use a release
in `musk1024/sub`, set `SUBCONVERTER_VERSION` in its Dockerfile to the published tag.
The archives retain the `subconverter/` directory expected by that Dockerfile.

The original desktop/32-bit build workflow remains available under
`Legacy cross-platform builds` as a manual workflow. The standalone Docker workflow
is also manual; it uses local source and requires its own Docker Hub credentials.
The Linux release pipeline does not depend on either legacy workflow.
