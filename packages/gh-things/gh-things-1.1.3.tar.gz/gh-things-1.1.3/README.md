# gh-things: Github things
**@readwithai** - [X](https://x.com/readwithai) - [blog](https://readwithai.substack.com/) - [machine-aided reading](https://www.reddit.com/r/machineAidedReading/) - [📖](https://readwithai.substack.com/p/what-is-reading-broadly-defined
)[⚡️](https://readwithai.substack.com/s/technical-miscellany)[🖋️](https://readwithai.substack.com/p/note-taking-with-obsidian-much-of)

A collection of command-line utilities to fetch information about "objects" in a machine-readable way (JSON) way.

## Motivation
I often interact with github. It is nice to be able to automate the things I am doing, or just do then from the shell. `gh` has some good functionality but some of the features are lacking and JSON output is based on extracting individual fields.

This repository is a dumping ground for various tools to fetch inforfmation from github. It wraps the `gh` tool (normally `gh api`) to avoid having to deal with authentication.

## Alternatives and prior work
The Github API is complete and can easily be called with `gh api`. You do however have to remember the API and read documentation when using it - which is fiddly for many tasks. This project provides a simpler and self-documenting interface to common parts of the api.

`gh` itself can often view objects with the `--json` and `--jq` methods.

## Installation
You can install `gh-things` using [pipx](https://github.com/pypa/pipx) with:
```
pipx instal gh-things
```

`gh-things` requires the [gh command-line tool](https://github.com/cli/cli).

## Usage
To get information about a repository you can run:

```
gh-things repo url
```

## Caveats
I will slowly add features here as I need them. I'll likely add methods for users and stargazers soon.

## About me
I am **@readwithai**. I create tools for reading, research and agency sometimes using the markdown editor [Obsidian](https://readwithai.substack.com/p/what-exactly-is-obsidian).

I also create a [stream of tools](https://readwithai.substack.com/p/my-productivity-tools) that are related to carrying out my work. As you are looking at this page, you might be interested in [gh-views](https://github.com/talwrii/gh-views) - a tool to get view statistics about a github page, [gh-star-timeline](https://github.com/talwrii/gh-star-timeline) which fetches and maintains star counts for a repository, or [symbolboard2](https://github.com/talwrii/symbolboard2) and alternative ergonomic keyboard layout.

I write about lots of things - including tools like this - on [X](https://x.com/readwithai).
My [blog](https://readwithai.substack.com/) is more about reading and research and agency.

[![@readwithai logo](./logo.png)](https://readwithai.substack.com/)
