# Terra Nanotech Discordbot Cogs<a name="terra-nanotech-discordbot-cogs"></a>

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/terra-nanotech/tn-nt-discordbot-cogs/master.svg)](https://results.pre-commit.ci/latest/github/terra-nanotech/tn-nt-discordbot-cogs/master)

A collection of cogs for
[AA-Discordbot](https://github.com/pvyParts/allianceauth-discordbot)

______________________________________________________________________

<!-- mdformat-toc start --slug=github --maxlevel=6 --minlevel=1 -->

- [Terra Nanotech Discordbot Cogs](#terra-nanotech-discordbot-cogs)
  - [Important Information](#important-information)
  - [Install](#install)

<!-- mdformat-toc end -->

______________________________________________________________________

## Important Information<a name="important-information"></a>

These Discord bot COGs are specially tailored for the corporation Terra Nanotech.
They are COGs of apps we use, so they fit our needs.

> **Note**
>
> If you install this app, you need to be aware that there will be
> no support for any kind of issues you might encounter, and you have to figure it out
> on your own.

## Install<a name="install"></a>

```shell
pip install tnnt-discordbot-cogs
```

In `local.py` right after `INSTALLED_APPS`:

```python
# Terra Nanotech Discordbot Cogs
INSTALLED_APPS += ["eveuniverse", "tnnt_discordbot_cogs"]
```

Run DB migrations and restart supervisor.
