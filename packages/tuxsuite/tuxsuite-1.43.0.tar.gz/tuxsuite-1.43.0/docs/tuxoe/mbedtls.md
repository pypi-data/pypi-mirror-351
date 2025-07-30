# Building Mbed-TLS for one configuration

Submit an Mbed-TLS build request using the tuxsuite command line interface. This will
wait for the build to complete before returning by default.

```shell
git clone https://gitlab.com/Linaro/tuxsuite
cd tuxsuite
tuxsuite bake submit examples/bitbake/mbed.json
```

The results
([build-definition.json](https://storage.tuxsuite.com/public/demo/demo/oebuilds/2KPNkSKe945G5KFhwQ3Cnp9HdwD/build-definition.json),
[logs](https://storage.tuxsuite.com/public/demo/demo/oebuilds/2KPNkSKe945G5KFhwQ3Cnp9HdwD/build.log), ...)
will be available at
[artifacts](https://storage.tuxsuite.com/public/demo/demo/oebuilds/2KPNkSKe945G5KFhwQ3Cnp9HdwD/)
under a unique and non-guessable URL.

## Build definition

Mbed-TLS uses build-definition to describe the build:
!!! info "Using repo"

    === "YAML"

        ```yaml
        container: tuxbake/mbedtls-ubuntu-16.04
        sources:
          mbedtls:
            url: https://github.com/Mbed-TLS/mbedtls
            branch: master
            cmds: ulimit -f 20971520 && export MBEDTLS_TEST_OUTCOME_FILE='outcome.csv' &&
              ./tests/scripts/all.sh --seed 8 build_armcc
        ```

    === "JSON"

        ```json
        {
          "container": "tuxbake/mbedtls-ubuntu-16.04",
          "sources": {
            "mbedtls": {
              "url": "https://github.com/Mbed-TLS/mbedtls",
              "branch": "master",
              "cmds": "ulimit -f 20971520 && export MBEDTLS_TEST_OUTCOME_FILE='outcome.csv' && ./tests/scripts/all.sh --seed 8 build_armcc"
            }
          }
        }
        ```

!!! warning
  Support for build definition files in JSON format is deprecated and will be removed in tuxsuite release v1.44.0 or not later than a release on 6th August, 2025. Please migrate to the YAML format. Build definition file artefacts in 'JSON' and 'YAML' format will be published prior to the deprecation. From >=v1.44.0 or the corresponding version after 6th August, 2025 only 'YAML' format build definition will be published."

### Build definition format

The build definition can include the following fields:

* `sources` (dictionary with a single item): should be mbedtls. url, branch or ref can be specified. cmds is the command used to do the specific build.
* `container`: Docker container used to do the build. Currently provided containers are tuxbake/mbedtls-ubuntu-16.04, tuxbake/mbedtls-ubuntu-18.04, tuxbake/mbedtls-ubuntu-20.04.

### Plan

The plan that does all the builds corresponding to CI for mbed-TLS for Linux is available in [mbed.yaml](https://gitlab.com/Linaro/tuxsuite/-/blob/master/examples/bitbake/mbed.yaml)

The result of the above plan that has done the full build is available in [mbed-results](https://tuxapi.tuxsuite.com/v1/groups/demo/projects/demo/plans/2KReAZr8wxioSqPzr2Fnst8gaop)
