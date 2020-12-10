# TypeConf

The goal of this library is to help developers build more robust systems for
academia as well as industry by avoiding configuration errors.

This is achieved by providing a library to build dynamic but typesafe configurations.


## Features
- Configuration checking through pydantic
- Super simple integration of alternatives for ablation studies
- Automatic CLI generation
- Better visibility which parameters were used and which not
- Testing of existing configurations to help maintain them


## Benefits
- No more bad awakings when a script fails because of wrong configuration
- Tracking of which configuration parameters were used and which not
- Easy and structured way to run ablation studies

## Config Priority
There are multiple ways to set a value in the configuration.
Conflicts are resolved in the following order (sorted in ascending order).

0. Declaration Default (These should avoided in the first place and should always
be overwritten by the configuration)
1. Config Default
2. Set as preset (either through cli or in config file)
3. Set through config file
4. Set through CLI
5. Set in code before parsing
6. Set in code after parsing (Can be prohibited by using pydantics (Faux Imutablility)[https://pydantic-docs.helpmanual.io/usage/models/#faux-immutability]
This is meant to reflect most common use cases.

## Installation
```python
pip install -e .
```
## Dependencies
- pydantic

## Examples
- MNIST
### Demo
- examples/Demo.ipynb


# TODO
## Features
- [ ] Easier integration of
    - [ ] classes
    - [ ] functions
    - [ ] libraries
- [ ] Own cli parser for better support
- [ ] Integrate into testing frameworks
- [ ] Fast Presets: Same kind of parameters as a specific class, just about hyperparameters
- [ ] click-style execution?

## Examples
- [ ] Ablation Study


## Open Questions
- [ ] Different namespaces for subclasses? For example, 
class2 inherits from class2, should they have a separate or joined namespace. See test.
- [ ] Should build method be abstract? Is there a use case, where a ChildConfig  
does not need a build method?

## CI/CD
- [x] versioneer
- [ ] Automatic testing on push
- [ ] black?
- [ ] push to pypi

## Documentation
- [ ] Write README
- [ ] Document Code
- [ ] Setup read the docs
