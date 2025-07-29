"""
This module contains task related commands for the QC client.
"""
from volcengine_qcclient import QcService, QcBatchJob
from prettytable import PrettyTable

from .utils import check_config


@check_config(['ak', 'sk', 'qc_service_id'])
def list_tasks(args, qc_config=None):
    """List all QcTasks of a QcService"""
    assert qc_config is not None, "QC configuration is not set. Please run 'volcqc configure' first."

    svc = QcService()
    svc.set_ak(qc_config['ak'])
    svc.set_sk(qc_config['sk'])
    qc_service_id = qc_config['qc_service_id']
    
    params = {
        'PageSize': args.page_size,
        'PageNumber': args.page_num,
        'QcServiceId': qc_service_id,   
    }
    if type(args.filter) is str and args.filter.strip() != '':
        params['NameContains'] = args.filter.strip()
    if hasattr(args, 'ids') and args.ids and isinstance(args.ids, list) and all(isinstance(i, str) for i in args.ids):
        params['Ids'] = args.ids
    result = svc.list_qc_tasks(params=params)    
    tasks = result.get('Items', [])
    if not tasks:
        print("No tasks found.")
        return
    
    full_columns = args.wide
    table = PrettyTable()
    field_names = ["TaskID", "Label", "TaskType", "Status", "MoleculeName"]
    if full_columns:
        #table.field_names.extend(["TaskConfig"])
        field_names.extend(["CreateTime", "StartTime", "EndTime"])
    table.field_names = field_names
    for task in tasks:
        fields = [
            task.get('Id', ''),
            task.get('Label', ''),
            task.get('TaskType', ''),
            task.get('Status', ''),
            task.get('MoleculeName', ''),
        ]
        if full_columns:
            #fields.extend([task.get('TaskConfig', '')])
            fields.extend([
                task.get('CreateTime', ''),
                task.get('StartTime', ''),
                task.get('EndTime', '')
            ])
        table.add_row(fields)
    print(table)

@check_config(['ak', 'sk', 'qc_service_id'])
def download_task_outputs(args, qc_config=None):
    assert qc_config is not None, "QC configuration is not set. Please run 'volcqc configure' first."

    task_id = args.id
    label = args.label
    if not label:
        svc = QcService()
        svc.set_ak(qc_config['ak'])
        svc.set_sk(qc_config['sk'])
        qc_service_id = qc_config['qc_service_id']

        params = {
            'QcServiceId': qc_service_id,
            'Ids': [task_id],
        }
        result = svc.list_qc_tasks(params=params)
        tasks = result.get('Items', [])
        if not tasks:
            print(f"Task {task_id} not found.")
            return
        label = tasks[0]['Label']

    batch_job = QcBatchJob(
        ak=qc_config['ak'], sk=qc_config['sk'], qc_service_id=qc_service_id, label=label
    )

    print(f'Downloading task {task_id}...')
    batch_job.wait()
    batch_job.download_outputs([task_id], target_dir=args.target_dir)
