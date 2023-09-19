Vertex pipelines will execute your components in a Docker image that you will need to specify. We recommend building a single base image that will embark all your python packages and codebase.
You could have as many images as you have components, each taylored and optimized to only embark the code and dependencies that you need, but that is excessively difficult and much less efficient to develop, deploy, and maintain.

## Use a single base image
Having a unique base image that serves as an execution environment for all your code and components has several advantages:


- The base image is extremely simple, and you will only ever have to write the Dockerfile once.
- You will only need one CI/CD to build and push that image to your image registry.
- It's easier to have a local environement identical to your image, reducing the risk of code working locally, but not in the pipeline.
- All your components will have the same boilerplate decorator, avoiding copy-paste errors and making the codebase more consistent.

## Exceptions to the rule
There are certain cases when it can be better to use a separate image for a specific operator.

- Operators that require a package that is not compatible with the rest of your base image. Maybe you need a different runtime than python, or you need an old version of a package that conflicts with the rest of your dependencies.
- Very large dependencies that would bloat the rest of your pipeline. If a dependency adds entire gigabytes to your base image, then it could be a good reason to dedicate another image for it. [Even then, prefer the method described here to add extra packages to a specific component.](managing_packages.md/#adding-a-package-in-a-single-component)

!!! warning ""
    These cases should be very rare. Even if you feel like 90% of what you put in the base image is unused by any single component, it does not cost anything for it to be there anyways. What is costly however, is building a new dedicated image which will require you to write a new Dockerfile, CI/CD, run tests, write doc, onboard others, and maintain it.