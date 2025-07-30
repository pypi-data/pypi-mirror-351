# nobuild
Distribution-independent custom image creation framework, inspired by [LUBS](https://lubs.fascode.net/).
## Purpose
## Target
- Creating an image creation framework that is independent of any particular distribution
- Easy to use
- Configuration file based on existing format
### Non-Target
- Generate multiple versions based on different distributions from a single project.
  - Directory structure may vary by distribution
- GUI frontend included
  - nobuild is not a remastering tool, and since the configuration files are already easy to read, there is no need for a GUI frontend, which would only lead to unnecessary bloat.