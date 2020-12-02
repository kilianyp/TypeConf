# TypeConf

The goal of this library is to help developers build more robust systems for
academia as well as industry by avoiding configuration errors.


## Features
- Configuration checking through pydantic
- Better visibility which parameters were used and which not
- Super simple integration of alternatives for ablation studies
- Testing of existing configurations to help maintain them


## Benefits
- No more bad awakings when a script fails because of wrong configuration
- Tracking of which configuration parameters were used and which not
- Easy and structured way to run ablation studies


## Installation
```python
pip install -e .
```
## Dependencies
- pydantic

## Examples
- MNIST


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
- [ ] versioneer
- [ ] Automatic testing on push
- [ ] black?
- [ ] push to pypi

## Documentation
- [ ] Write README
- [ ] Document Code
- [ ] Setup read the docs