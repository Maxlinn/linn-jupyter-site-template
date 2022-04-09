# Homepage

Set up you jupyter-markdown hybrid site in one minute, powered by [Docsify](https://docsify.js.org/).

Your :star: would be high praise for my efforts, thank you!

This project is based on [Maxlinn's Docsify Template Demo](https://maxlinn.github.io/linn-docsify-template).

**Anytime you want to quote some `notebook.ipynb`, use `notebook.md` instead, because `.ipynb` will be transformed into `.md` later on.**

## Usage

- Use this repository as template.
  - You'll get a `main` branch with those files.
  - To modify:
    - `index.html`, settings, **must modify, at least modify those commented with `!!!`**.
    - `README.md`, homepage of your site, **change it to yours**.
    - `_navbar.md, _sidebar.md, _footer.md`, **change it to yours**. Remove any if you don't like.
    - `favicon.svg`, the icon your site, **change it to yours**. To use other format, edit `index.html`.
  - To remove:
    - Folder `a-great-subfoloder`, just for demo, **remove it and its contents**.
    - `NOTEBOOK.ipynb`, just for demo, **remove it**.
  - Nevermind:
    - `.nojekyll`, nevermind.
- Go to repository settings, set `github pages` work on `main` branch.
- Done!

## Reminder

- `README.md` of each folder level would serve as homepage of this level, like this one you are reading. 
  - So don't hesitate to change this `README.md` to create your own homepage!
- The sidebar serve as a document navigator as well as `table of contents` of current document.
  - The sidebar item starts with an `-` belongs to `table of contents` of current document.
  - Other sidebar items are defined in `_sidebar.md`.
- To disable features, comment its plugin `<script>` tag inside `index.html`.

## Features

Powered by [plugins of docsify](https://docsify.js.org/#/plugins), and [community contributions](https://docsify.js.org/#/awesome?id=awesome-docsify-).

- Full text search.
  - Discover documents by hyperlinks of the documents you viewed, like a web spider.
  - Implemented just in frontend.
  - **Not always index all documents of this site**.
  - Search index rebuilt every one day by default, stored in localstorage.
- Dark mode switch button.
- LaTeX, mermaid.js, code highlight support.
- Custom font settings.
- User experience enhancement.
  - Copy code button.
  - PanGu, add space when Chinese and English characters drawing near.
  - Collapsable nested sidebar.
- Support [tabs syntax](https://jhildenbiddle.github.io/docsify-tabs/#/?id=usage), see examples in syntax test below.