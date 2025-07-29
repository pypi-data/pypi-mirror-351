# aa-wiki

Wiki plugin for [AllianceAuth](https://gitlab.com/allianceauth/allianceauth) to curate content.

## Features

- Create and organise pages in a hierarchical structure using `slugs`
- Supports markdown with both rich and raw editing modes
- Version History
- Event logging
- Restrict content by user's `groups` and/or `states`

## Permissions

Users need to have at least `basic_access` interactions with the application

| Name                  | Description                                              |
|-----------------------|----------------------------------------------------------|
| `basic_access`        | Basic access to load content                             |
| `editor_access`       | Grant the necessary controls and access to edit content  |


## Settings

List of settings that can be modified for the application
You can alter them by adding a record to the `Settings` section/table in the `evewiki` section of the Admin site

| Name                          | Description                                                                                      | Default |
|-------------------------------|--------------------------------------------------------------------------------------------------|---------|
| `hierarchy_max_display_depth` | Limit the depth of the tree for the hierarchy on the main display                                | 10      |
| `max_versions`                | No one has infinite disk space, a sensible limit which can be modified to clear down the history | 1000    |

## Installation !!! NOT WORKING !!!

> Currently produces an error!!!

### Step 1 - Pre_Requisites

Evewiki is an App for Alliance Auth, Please make sure you have this installed. Evewiki is not a standalone Django Application

### Step 2 - Install app

pip install evewiki

### Step 3 - Configure Auth settings

Configure your Auth settings (`local.py`) as follows:

- Add the following `INSTALLED_APPS` in `local.py`

```plaintext
'evewiki',
```

## Development

> This has instructions on how to circumvent the installation issue on a dev environment

*Assumes setup of AA as per the [documentation](https://allianceauth.readthedocs.io/en/latest/installation-containerized/docker.html)*
Final folder structure would look like
```plaintext
aa-dev
├─ aa-docker
└─ aa-wiki

```

Traverse into the `aa-dev` folder and clone the repo
```bash
git clone https://gitlab.com/cunningdesigns/aa-wiki.git
```

Traverse to `../aa-docker` folder

Bind-mount the plugin-folder in `aa-docker/docker-compose.yml`
```yaml
x-allianceauth-base:
  volumes:
    - ../aa-wiki:/home/allianceauth/evewiki
```

___
*there has to be a better way*
> Replace `aa-wiki/evewiki/views.py` with content from [example plugin](https://gitlab.com/ErikKalkoken/allianceauth-example-plugin/-/blob/master/example/views.py?ref_type=heads)

> Comment out lines 11,12 & 14 on `aa-wiki/evewiki/urls.py`
___

Start the containers (may require sudo)
```bash
docker compose --env-file=.env up -d
```

Open a terminal in the gunicorn container, initiate the plugin install
```bash
docker compose exec allianceauth_gunicorn bash
pip install -e ../evewiki
```

add `evewiki` to `aa-docker/conf/local.py`

Apply migrations and exit
```bash
python manage.py migrate
```

restart AA
```bash
docker compose restart allianceauth_gunicorn
```

___
*there has to be a better way*
> Remember to undo the modifications to `evewiki/evewiki/views.py` & `evewiki/evewiki/urls.py`
___
