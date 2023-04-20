This repository template is meant to help Vertex pipelines beginners understand and avoid its pitfalls. It illustrates what we find is the most efficient way to transition from notebook exploration to a reliable, industrialized ML pipeline.

It is based on the collective knowledge and feedbacks of past Artefact projects and people. It is meant to illustrate an architecture that provides both iteration/exploration speed, as well as reliability for industrialisation.

It also touches on patterns that we have seen not work well or had worse velocity and reliability in our experience.

# Understanding the Vertex AI platform
# Vertex pipelines
## Convictions

## Other things
- Use a single base docker image for all components
- Use function-based components
- Embark as little intelligence as possible in the components
- Have the intelligence concentrated in a regular python folder/files structure
- This code should be locally executable for quick iteration

## Phase 1 - Notebook exploration

- Wrap code in functions -> they will be easily transferable to scripts
- Type hint functions inputs/outputs -> Will help make sure types will be vertex-compatible
- Build your Notebook in a way that will mirror an ML pipeline: a section for a pipeline step/component

## Phase 2 - Refactor to a regular python project

- Migrate from notebooks to scripts
- Have clear entrypoint functions to then use in components
- Run scripts locally to make sure everything works as expected
- Run scripts locally to make sure they work as intended
- Maybe even write a few unit/integration tests
- Have a fully functional workflow before even thinking of moving to Vertex

## Phase 3 - Wrap this code in components and pipelines

