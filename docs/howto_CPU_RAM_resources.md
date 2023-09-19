
!!! example ""
    In the following example, `flip_coin` is a component object.

    ```python3
    @dsl.pipeline
    def my_pipeline():
        coin_flip_task = flip_coin() \
            .set_cpu_limit(8) \
            .set_memory_limit("16G") \
            .add_node_selector_constraint("NVIDIA_TESLA_K80") \
            .set_gpu_limit(2)
    ```

Reference: https://cloud.google.com/vertex-ai/docs/pipelines/machine-types