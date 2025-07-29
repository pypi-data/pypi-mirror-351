# Crux command line tool - cruxctl

Herein contains the source code for the cruxctl command line tool. It is used to submit jobs, validate YAML
files, and manipulate deadlines related to Crux. 

The repositories related to it are [cruxctl](https://github.com/cruxinformatics/cruxctl/releases) 
and [crux-odin](https://github.com/cruxinformatics/crux-odin/releases) (a library used by `cruxctl`).

<img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue" />
<img src="https://img.shields.io/badge/YAML-green" />
<img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white" />
<img src="https://img.shields.io/badge/Airflow-017CEE?style=for-the-badge&logo=Apache%20Airflow&logoColor=white" />

## Installation

You install `cruxctl` via PyPI and `pip` in any Python environment you wish. You can install
it in a `venv` environment, a `pipenv` environment, or a `poetry` environment. You can also install it
at the system level if you wish. The installation doesn't vary from any other Python package. Just do
a `pip install cruxctl` or `pip install cruxctl==<version>` and you're good to go. It does require
that you can authenticate with Google Cloud and have the proper permissions to access the Crux API.
It also requires that you have a login on the Crux system so you can get a token. Type `cruxctl --help`
for command help and `cruxctl <command> --help` for subcommand help.

## Usage

Authorize with `cruxctl auth`. `cruxctl auth --help` will get you started with authorization.

### Examples for AI Schedule

Get calculated delivery deadline:
```
cruxctl ai-schedule get-delivery-deadline -d AQKwpurp8B-G848Qqs7JthWOog -bm 60
```

### Example for AI curation

Onboard data through Crux - run through profiler, upload vendor doc. These would trigger curation to run on event based. After profiling is done, you are now able to download odin yaml. You can check the odin file against curation output using cruxctl command. 

```
cruxctl dataset update -f [ODIN_YAML_FILE]
  --profile [ENVIRONMENT] --from-docs
```

### Examples for Deadline Management

See available commands and help:
```shell
cruxctl deadlines --help
```

Get all deadlines:
```shell
cruxctl deadlines get-all
```

Get a specific deadline:
```shell
cruxctl deadlines get dataset-id-abc
```

Insert a deadline:
```shell
cruxctl deadlines insert dataset-id-abc  0 23 '3W' '*' '*' '*'
```

Delete deadlines matching dataset ID:
```shell
cruxctl deadlines delete dataset-id-abc
```

Delete all deadlines:
```shell
cruxctl deadlines delete-all dataset-id-abc
```

Import deadlines from CSV:
```shell
cruxctl deadlines import /path/to/file/deadlines.csv
```

Export deadlines to GCS bucket as CSV file:
```shell
cruxctl deadlines export gs://my-bucket/deadlines.csv
```

Get all notification snoozes:
```shell
cruxctl deadlines get-all-notification-snooze
```

Get a specific notification snooze:
```shell
cruxctl deadlines get-notification-snooze dataset-id-abc
```

Create a notification snooze:
```shell
cruxctl deadlines create-notification-snooze dataset-id-abc 72 hours
```

Delete a notification snooze:
```shell
cruxctl deadlines delete-notification-snooze dataset-id-abc
```

Delete expired notification snooze(s):
```shell
cruxctl deadlines delete-expired-notification-snooze
```

### Example for YAML Validation

Validate YAML files which possibly point to a parent YAML file. 
There are two forms: one where you just give the YAML file names and the other
where you give a start directory and the YAML file names. The second form exists
because normally the data engineers stick the YAML files below a directory named
after the company. They also often put a parent YAML file there too and a bunch
of child YAML files refer to it. Therefore, we allow the user to pass this directory
as the first argument and the child or parent files as the subsequent arguments.
If you modify the child file and there is a parent, the combined parent/child
YAML is validated. If you pass a parent file, ALL THE CHILDREN of that parent
file are validated.

You can also pass a parent file and a child file with the first form where you
just give YAML paths. In this case, pass the parent and the child YAML file
as the same argument separated by a comma. For example

```shell
cruxctl dataset validate a.yaml b.yaml,c.yaml
```
validates `a.yaml` by itself and the combined `b.yaml/c.yaml`. This supposes
that `b.yaml` is the "parent" of `c.yaml`.

The full usage syntax is:
```shell
cruxctl dataset validate [--profile local|dev|staging|prod] [--quiet] file_or_dir yaml_file...
```
Normally `cruxctl dataset validate` prints out the progress as it goes. `--quiet` turns this off.

### Example for deploying an Odin dataset to the control plane

To deploy an Odin dataset YAML file to the control plane, give one or more arguments to
the `dataset apply` command. This command can deploy multiple YAML files from one command
line invocation if you give multiple YAML files to apply. Like the `dataset validate` command,
you can give a directory as the first argument and YAML files to apply after that or you can
just give the YAML files to apply (or combined YAML files separated by commas. See the
`dataset validate` command for syntax).

Usage:
```shell
cruxctl dataset apply [--profile local|dev|staging|prod] [--quiet] [--cluster oss|composer] [--region us-central1|us-east1] [--shard 0|1|2|3|4|5|6|a|b|c|d|e] file_or_dir yaml_file...
```
Applying starts the processing runs for the YAML files. Normally it prints out as it
is applying the YAML files. Use `--quiet` to turn this off.

The `--cluster` option is used to specify the cluster type: `oss` or Cloud Composer. The
default is `oss`.

The `--region` option is used to specify the region for the Airflow run. The default
is `us-central1`.

The `--shard` option is used to specify the shard for the Airflow deployment. The default
is `0`.

### Example for deleting a dataset in the control plane

If you'd like to delete an existing dataset(s) in the control plane, give the following command:

```shell
cruxctl dataset delete [--profile local|dev|staging|prod] [--quiet] dataset_id...
```

### Example for getting the events from a deployed dataset

To see the events from a deployed dataset, give the following command:
```shell
cruxctl dataset events [--watch] [--environment local|dev|staging|prod] dataset_id
```
This prints out the events for that dataset ID. If you give the `--watch` option,
then every three second more output is checked for an output. The output looks like
this:
```json
{'specversion': '1.0', 'type': 'com.crux.cp.dataset.ingest.apply.v1', 'source': '/apilayer', 'subject': '', 'id': 'e0e1936d-e70b-4351-95e4-66fbefbbdf8b', 'time': '2024-09-10T22:39:57.077029Z', 'data': {'id': 0, 'datasetId': 'DssgxkJB', 'orgId': 'test', 'eventId': 'e0e1936d-e70b-4351-95e4-66fbefbbdf8b', 'eventSource': '/apilayer', 'eventType': 'com.crux.cp.dataset.ingest.apply.v1', 'message': 'validation pass', 'statusType': 'Apply'}}
{'specversion': '1.0', 'type': 'com.crux.cp.dataset.ingest.apply.v1', 'source': '/apilayer', 'subject': '', 'id': 'e69b7204-2cff-4702-a65e-885bb7f77d7d', 'time': '2024-09-10T21:31:01.843591Z', 'data': {'id': 0, 'datasetId': 'DssgxkJB', 'orgId': 'test', 'eventId': 'e69b7204-2cff-4702-a65e-885bb7f77d7d', 'eventSource': '/apilayer', 'eventType': 'com.crux.cp.dataset.ingest.apply.v1', 'message': 'validation pass', 'statusType': 'Apply'}}
{'specversion': '1.0', 'type': 'com.crux.cp.dataset.ingest.apply.v1', 'source': '/apilayer', 'subject': '', 'id': 'f41f54e3-b9d2-4638-a766-69662c75fbc4', 'time': '2024-09-10T21:59:00.67005Z', 'data': {'id': 0, 'datasetId': 'DssgxkJB', 'orgId': 'test', 'eventId': 'f41f54e3-b9d2-4638-a766-69662c75fbc4', 'eventSource': '/apilayer', 'eventType': 'com.crux.cp.dataset.ingest.apply.v1', 'message': 'validation pass', 'statusType': 'Apply'}}
```
### Example for retrieving dataset's PDK logs

If you'd like to retrieve pdk logs of an existing dataset in the control plane, run the following command:

```shell
cruxctl dataset pdk-logs [DATASET_ID] --delivery-id [DELIVERY_ID]
```

### Example for retrieving dataset's dispatch logs

If you'd like to retrieve dispatch logs of an existing dataset in the control plane, run the following command:

```shell
cruxctl dataset dispatch-logs [DATASET_ID] --export-id [EXPORT_ID]
```

## Thanks to all the contributors:
[//]: <> (cruxctl isn't open source yet. When it is, go to contrib.rocks and regenerate the URL and insert below.)
<a href="https://github.com/cruxinformatics/cruxctl/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=cruxinformatics/cruxctl" />
</a>
