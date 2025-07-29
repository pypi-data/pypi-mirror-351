## v3.11.0 (2025-05-28)

### ✨ Features

- **imagetool:** add "Edit Coordinates" option ([24e8875](https://github.com/kmnhan/erlabpy/commit/24e887558ef9395965f260e5b8b2e946cf0352ca))

  Adds a new feature to ImageTool that allows users to edit the coordinates directly. The new dialog can be accessed via `Edit Coordinates` in the `Edit` menu.

- **io.igor:** add functions to read igor text files (#142) ([1075b1e](https://github.com/kmnhan/erlabpy/commit/1075b1e7a499c556d2388d21e4ca195c1500e3ae))

  Also adds a data loader plugin for the spin-ARPES setup (system 1) at Seoul National University.

- **imagetool.manager:** add check for invalid python identifiers when storing data with iPython ([f3bf529](https://github.com/kmnhan/erlabpy/commit/f3bf529ce3e31cf2df133a0ea0f857fb50dd04aa))

- **io:** add data loader for ALS BL10.0.1 HERS ([4945fe7](https://github.com/kmnhan/erlabpy/commit/4945fe76b68f1e954a9358b9df6bfd4645584e84))

### 🐞 Bug Fixes

- **imagetool:** preserve coordinate order displayed in repr ([d54462c](https://github.com/kmnhan/erlabpy/commit/d54462c4a4db7647f2859ad83b1c5cd5c1a0b383))

- **imagetool.manager:** improve taskbar grouping on Windows ([ae86938](https://github.com/kmnhan/erlabpy/commit/ae86938d923d8cbe72bcff3bd69ec90f5acca9e3))

- **interactive:** correctly show exceptions raised during initializing interactive tools ([75fd45e](https://github.com/kmnhan/erlabpy/commit/75fd45e37df1a3d2d0c5e48071d9c29c6120761b))

- **imagetool:** correctly display error message for undefined selection code in 2D data ([6a1b276](https://github.com/kmnhan/erlabpy/commit/6a1b2760630eef535e591d8e7fd40e1741121657))

- **analysis.image:** allow N-dimensional input to 2D curvature ([83048b9](https://github.com/kmnhan/erlabpy/commit/83048b955d9684dc4d6f0c5ec476c5ed323cd06b))

  Allow N-dimensional input to 2D curvature function. The curvature is computed for the first two dimensions.

[main 4102bd2] bump: version 3.10.2 → 3.11.0
 3 files changed, 9 insertions(+), 3 deletions(-)

