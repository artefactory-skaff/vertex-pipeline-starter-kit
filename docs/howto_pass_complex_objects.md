
Vertex components only allow you to use `dict`, `list`, `int`, `float`, `string`, and `bool` as input and output parameters. 

You are probably going to want to pass more complex, or custom types to your components. For this you will need to pass them using Artifacts.

## Artifacts

Although you can not directly pass complex types directly, components can produce Artifacts as outputs that may then be used as inputs in other components.


!!! example "Save and load an artifact"
    ```python3
    @component
    def first_component(artifact: Output[Artifact]):
        # Component logic that creates data here
        data = "..."
        with open(artifact.path, "w+") as output_file:
            artifact_contents = output_file.write(data)
    ```

    ```python3
    @component
    def second_component(artifact: Input[Artifact]):
        with open(artifact.path, "r") as input_file:
            artifact_contents = input_file.read()
            print(f"artifact contents: {artifact_contents}")
        # Component logic that uses data here
    ```

The `Artifact` type is generic and flexible. There are more specialized types (`Model`, `Dataset`, `Markdown`, ...) that you should use when relevant. [Artifact types](https://github.com/kubeflow/pipelines/blob/sdk/release-1.8/sdk/python/kfp/dsl/io_types.py)

If you need to pass custom types, consider saving then as a pickle file.

## References

- [lightweight_functions_component_io_kfp](https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/official/pipelines/lightweight_functions_component_io_kfp.ipynb)