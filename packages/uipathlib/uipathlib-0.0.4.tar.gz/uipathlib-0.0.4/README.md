# uipathlib

* [Description](#package-description)
* [Usage](#usage)
* [Installation](#installation)
* [License](#license)

## Package Description

UiPath Cloud client Python package that uses the [requests](https://pypi.org/project/requests/) library.

> [!IMPORTANT]
> This packages uses pydantic~=1.0!

## Usage

* [uipathlib](#uipathlib)

from a script:

```python
import uipathlib

url_base = "https://cloud.uipath.com/mycompany/production/orchestrator_"
client_id = "ABX"
refresh_token = "ABD"
fid = "12"
bucket_id = "123"

uipath = UiPath(url_base=url_base,
                client_id=client_id,
                refresh_token=refresh_token)
```

```python
# ASSETS
response = uipath.list_assets(fid=fid)
if response.status_code == 200:
    df = pd.DataFrame([item.dict() for item in response.content])
    print(df)
```

```python
# BUCKETS
response = uipath.list_buckets(fid=fid)
if response.status_code == 200:
    df = pd.DataFrame([item.dict() for item in response.content])
    print(df)
```

```python
response = uipath.create_bucket(fid=fid,
                                name="Test 5",
                                identifier="a1111111-dc1c-1111-111c-111c11ef1111",
                                description="Test description 5")
print(response.status_code)
```

```python
# UPLOAD
response = uipath.upload_bucket_file(fid=fid,
                                     id=bucket_id, 
                                     localpath=r"C:\Users\admin\Desktop\My bucket 3.txt", 
                                     remotepath=r"My bucket 3.txt")
print(response.status_code)
```

```python
# DELETE
response = uipath.delete_bucket_file(fid=fid,
                                     id=bucket_id, 
                                     filename=r"My bucket 3.txt")
print(response.status_code)
```

```python
# CALENDARS
response = uipath.list_calendars(fid=fid)
if response.status_code == 200:
    df = pd.DataFrame([item.dict() for item in response.content])
    print(df)
```

```python
# ENVIRONMENTS (UNDER DEVELOPMENT)
response = uipath.list_environments(fid=fid)
if response.status_code == 200:
    df = pd.DataFrame([item.dict() for item in response.content])
    print(df)
```

```python
# JOBS
response = uipath.list_jobs(fid=fid, filter="State eq 'Running'")
if response.status_code == 200:
    df = pd.DataFrame([item.dict() for item in response.content])
    print(df)
```

```python
response = uipath.start_job(fid=fid, 
                            robot_id="123", 
                            process_key="Process_A")
if response.status_code == 201:
    print(response.content)
```

```python
# MACHINES
response = uipath.list_machines(fid=fid)
if response.status_code == 200:
    df = pd.DataFrame([item.dict() for item in response.content])
    print(df)
```

```python
# PROCESSES
response = uipath.list_processes(fid=fid)
if response.status_code == 200:
    df = pd.DataFrame([item.dict() for item in response.content])
    print(df)
```

```python
# QUEUES
response = uipath.list_queues(fid=fid)
if response.status_code == 200:
    df = pd.DataFrame([item.dict() for item in response.content])
    print(df)
```

```python
response = uipath.list_queue_items(fid=fid, 
                                   filter="QueueDefinitionId eq 275435")
if response.status_code == 200:
    df = pd.DataFrame([item.dict() for item in response.content])
    print(df)
```

```python
queue_item_id = "836491474"
response = uipath.get_queue_item(fid=fid,
                                 id=queue_item_id)
if response.status_code == 200:
    print(response.content)
```

```python
response = uipath.add_queue_item(fid=fid,
                                 queue="Queue_A",
                                 content={"EmployeeId": "12345",
                                          "RowId": "566829607423876",
                                          "State": "Approved",
                                          "RequestId": "LR00001",
                                          "Language": "English"},
                                 reference="12345",
                                 priority="Normal")
if response.status_code == 201:
    print(response.content)
```

```python
queue_item_id = "870192396"
response = uipath.update_queue_item(fid=fid,
                                    queue="Queue_A",
                                    id=queue_item_id,
                                    content={"EmployeeId": "12345",
                                             "RowId": "566829607423876",
                                             "State": "Approved",
                                             "RequestId": "LR00001",
                                             "Language": "12345"})
if response.status_code == 200:
    print("Done")
```

```python
queue_item_id = "870192396"
response = uipath.delete_queue_item(fid=fid,
                                    id=queue_item_id)
if response.status_code == 204:
    print("Done")
```

```python
# RELEASES
response = uipath.list_releases(fid=fid)
if response.status_code == 200:
    df = pd.DataFrame([item.dict() for item in response.content])
    print(df)
```

```python
# UNDER DEVELOPMENT!
get_release_process_key = "Queue_A"
response = uipath.get_release_process_key(fid=fid,
                                          name=get_release_process_key)
if response.status_code == 200:
    print(response.content)
```

```python
# ROBOTS
fid = "1138051"
response = uipath.list_robots(fid=fid)
if response.status_code == 200:
    df = pd.DataFrame([item.dict() for item in response.content])
    print(df)
```

```python
response = uipath.list_robot_logs(fid=fid, filter="JobKey eq a111d111-b111-1f11-b11d-111adac1111d")
if response.status_code == 200:
    df = pd.DataFrame([item.dict() for item in response.content])
    print(df)
```

```python
# UNDER DEVELOPMENT!
response = uipath.get_robot_id(fid=fid, name="ABC")
if response.status_code == 200:
    print(response.content)
```

```python
# ROLES
response = uipath.list_roles()
if response.status_code == 200:
    df = pd.DataFrame([item.dict() for item in response.content])
    print(df)
```

```python
# SCHEDULES
response = uipath.list_schedules(fid=fid)
if response.status_code == 200:
    df = pd.DataFrame([item.dict() for item in response.content])
    print(df)
```

```python
# SESSIONS
response = uipath.list_sessions(fid=fid)
if response.status_code == 200:
    df = pd.DataFrame([item.dict() for item in response.content])
    print(df)
```

## Installation

* [uipathlib](#uipathlib)

Install python and pip if you have not already.

Then run:

```bash
pip install pip --upgrade
```

For production:

```bash
pip install uipathlib
```

This will install the package and all of it's python dependencies.

If you want to install the project for development:

```bash
git clone https://github.com/aghuttun/uipathlib.git
cd uipathlib
pip install -e ".[dev]"
```

To test the development package: [Testing](#testing)

## License

* [uipathlib](#uipathlib)

BSD License (see license file)
