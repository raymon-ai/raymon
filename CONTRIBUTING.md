# License
[All contributions fall under the repository license.](https://docs.github.com/en/github/site-policy/github-terms-of-service#6-contributions-under-repository-license)


# Releasing
We use bumpversion to manage releases. 

1. Install the dev requirements. This will install bumpversion.
2. To bump version do: `bumpversion build` to create a new rc. To make a new prod release, use `bumpversion kind`. To continue with a new rc, use `bumpversion patch`

# Docs
We use Numpy style for writing docstrings.
We build library API docs with sphinx and publish it on github pages.

Building the docs works by running `make github` from the `docsrc` folder.

