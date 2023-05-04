There are a few pre-made Vertex AI components available as python packages through the google-cloud-pipeline-components SDK.

- [Homepage](https://pypi.org/project/google-cloud-pipeline-components/)
- [Actual docs](https://google-cloud-pipeline-components.readthedocs.io/en/google-cloud-pipeline-components-1.0.41/google_cloud_pipeline_components.v1.html)

They provide component interfaces for the rest of the Vertex AI platform, BQ ML, or AutoML that makes it easier to integrate them in pipelines. These can be used to quickly put together a walking skeleton. However, be aware of some limitations when using these pre-made components.

- They are not executable locally. This means that iteration time using these components will be fairly long compared to a homemade implementation.
- The level of abstraction they provide is small. They typically only wrap an already existing GCP API method in a component.
- This introduces black boxes in your pipeline. It will be more difficult to dive into the internals to debug.
- They're not very well documented.

Given this limitations we do not recommend using the components that only serve as wrapper for a well functioning python API (hence replacing only few lines of codes) as for those cases we feel the loss of not being able to run locally is not worth it compare to the gains. 

However for some uses cases  (ex: batch predictions), pre-made components can actually save you a lot of time so knowing about these components, and potentially integrating them in your pipelines can be a great idea and save some precious time despite their limitations. 
Make sure you read their docs thoroughly to ensure they do what you need them to and limit integration risks.

