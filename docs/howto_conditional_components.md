
You can control whether a component is executed or not using a `dsl.Condition`.

!!! example ""
    In the following example, `flip_coin` and `my_comp` are both component objects.

    ```python3
    @dsl.pipeline
    def my_pipeline():
        coin_flip_task = flip_coin()
        with dsl.Condition(coin_flip_task.output == 'heads'):
            conditional_task = my_comp()
    ```

## Reference

- [Vertex notebook example](https://github.com/GoogleCloudPlatform/vertex-ai-samples/blob/main/notebooks/official/pipelines/control_flow_kfp.ipynb)
- [Kubeflow control flow doc](https://www.kubeflow.org/docs/components/pipelines/v2/pipelines/control-flow/)