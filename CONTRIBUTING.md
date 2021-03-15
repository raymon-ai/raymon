# Releasing
We use bumpversion to manage releases. 

1. Install the dev requirements. This will install bumpversion.
2. To bump version do: `bumpversion build` to create a new rc. To make a new prod release, use `bumpversion kind`. To continue with a new rc, use `bumpversion patch`

