Assuming you are working with function-based components only and one docker base image, there are two ways for you to make python packages available in components.

## Adding globally available packages.

As all the components use the same base docker image, installing a package there will make it available in your code in all the components.

So, to add packages, do the following:

- Add whatever packages + version constraints you want in the `requirements.txt` file used to build the docker base image
- Rebuild your docker image with the new requirements (`make build_image`)

This is the preferred way of doing things in most situations. It ensures that your dependencies versions are consistent in your local env and across components and pipelines, reducing compatibilities issues. 

Having unused packages in a component my sound sub-optimal, but it is generally not an issue.

However, if you need a very cumbersome library for a specific component (e.g. pytorch, tensorflow, or other) you can surgically insert it like so:

## Adding a package in a single component.

!!! warning ""
    This method has a few drawbacks. It creates additional overhead when starting the component due to the time it takes to install the dependency. It will also cause pipelines to fail if package installation fails for whatever reason. This is less desirable than failing fast at the docker image building step. Finally, overusing this will also decrease the overall coherence of your codebase and running different steps with different packages/version may have undesired consequences.

In a component file:

!!! example "my_component.py"

    ```python3
    from kfp.v2.dsl import component

    @component(
        base_image=f"eu.gcr.io/{os.getenv("PROJECT_ID")}/vertex-pipelines-base:latest",
        packages_to_install=["torch==2.0.0"]  # Installs pytorch specifically for this component.
    )
    def my_component():
        # Do things
        pass
    ```