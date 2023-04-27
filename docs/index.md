This repository template is meant to help Vertex pipelines beginners understand and avoid its pitfalls. It illustrates what we find is the most efficient way to transition from notebook exploration to a reliable, industrialized ML pipeline.

It is based on the collective knowledge and feedbacks of past Artefact projects and people. It is meant to illustrate an architecture that provides both iteration/exploration speed, as well as reliability for industrialisation.

It also touches on patterns that we have seen not work well or had worse velocity and reliability in our experience.

# Understanding the Vertex AI platform

Before we start, it is important to mention the difference between Vertex AI and Vertex AI Pipelines. Vertex AI is a set of services gathered in a unified service called "Vertex AI" (e.g. Vertex AI Dataset, Vertex AI Pipelines, Vertex AI endpoints, etc.). As you can see, Vertex AI Pipelines is simply a service included in the Vertex AI environment.

Have you been hearing about Vertex AI Pipelines for months without really understanding what it is?


# Vertex pipelines

So, what are Vertex AI Pipelines?

Vertex AI Pipelines is a managed service offered by GCP to execute Kubeflow Pipelines.

If you separate all your machine learning workflow into “components” representing each steps of your ML workflow, then you can write your workflow using Kubeflow Pipelines SDK. In return, Kubeflow Pipeline makes your workflow portable and scalable.

Vertex AI Pipeline is a managed service to run your Kubeflow Pipelines.


## Convictions

Our main conviction is that Vertex AI pipelines are overall a pain to work with, and that you should reduce as much as possible the amount of interaction you have with them.

There are two big issues that we address with this starter kit:

- Vertex Pipelines have a high execution time overhead. Your code in a pipeline component will have an incompressible 2 minutes startup time. While it does not look like a lot, it absolutely kills development velocity and cycle time. You can not iterate quickly with a 2 minutes overhead for each execution.
- Vertex Pipelines are very flexible and there are many ways to develop with them. Too many. Here we try to provide one way of working with the tool that reduces the pain of industrialisation while preserving iteration speed during the exploration, development, and evolution of your ML pipeline.


Here are our recommendation to avoid the problems above:

- Use a single base docker image for all components
- Only use function-based components
- Embark as little intelligence as possible in the components
- Have the intelligence concentrated in a regular python folder/files structure
- This code should be locally executable for quick iteration

# Process for working with Vertex pipelines

## Phase 1 - Notebook exploration
- Do your usual notebook things, maybe start thinking about writing functions, but no pressure.

## Phase 2 - Refactor your notebook for it to look like a pipeline

- Wrap code in functions to make them easily transferable to scripts
- Write your Notebook in a way that will mirror an ML pipeline: a section for a pipeline step/component, the notebook itself could represent the pipeline.
- When loading data from files, or tables to pandas dataframe, make sure to explicitly cast to the types that you will use. Vertex has a way of loading data that may produce similar but different data types.
- Type hint functions inputs/outputs as a general good practice and to identify at a glance the vertex-compatible ones

## Phase 3 - Refactor to a regular python project

- Migrate from notebooks to scripts
- Have clear entrypoint functions to then use in components
- Run scripts locally to make sure everything works as expected
- Run scripts locally to make sure they work as intended
- Maybe even write a few unit/integration tests
- Have a fully functional workflow before even thinking of moving to Vertex Pipelines

## Phase 4 - Wrap this code in components and pipelines

- In components, import and call your top-level functions. Again, if you find yourself writing business or technical logic in the component, you should think about moving it to your `lib`
- Finally, you can compose your pipeline from the components that you defined.
- Run your pipeline, and hope for the best.

## Phase 5 - Iterate and improve

You are probably going to need to go back to phase 1 to iterate and go through the motions again, from notebook to running pipeline. This is expected and normal. Doing it often will make you think end-to-end and allow you to close the feedback loop with users, thus limiting tunnel effect. It will also highlight potential integration risks within and around the pipeline early on. See: Walking skeleton approach.