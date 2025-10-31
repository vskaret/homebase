# How to use tailwind cli

If already setup, run

`./tailwindcss --input input.css --output output.css --watch`

## Installation (for ubuntu)

Download tailwind-cli (you're free to change `v4.0.0` to which version you want, probably the latest - see [releases](https://github.com/tailwindlabs/tailwindcss/releases/))

`curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/download/v4.0.0/tailwindcss-linux-x64`

Make it executable

`chmod u+x tailwindcss-linux-x64`

Rename file

`mv tailwindcss-linux-x64 tailwindcss`

Now, the tailwind-cli needs an input css file that imports tailwind and specifies where to look for html files. It also needs an output css file where it generates all of the css code.

In this project our `input.css` file looks as follows

```css
@import "tailwindcss" source("../../templates/**");
```

imports `tailwindcss` from the current directory and looks in the `templates` directory and all sub-directories for html files.

Now start up with

`./tailwindcss --input input.css --output output.css --watch`

The `--watch` options tells the tailwind program to remake the output css anytime a html file has been changed (or something like that). For this to work, the django third party app [`django-browser-reload`](https://github.com/adamchainz/django-browser-reload) must be installed.
