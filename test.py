from datas import Task, ExcelInfo

if __name__ == "__main__":
    task_ids = list(map(int, input().split()))
    tasks = []

    for task_id in task_ids:
        task_instance = Task(task_id)
        task = ExcelInfo(task_id, task_instance.time, task_instance.machine.name, task_instance.machine.region, task_instance.driver.driver_name, task_instance.work_type.work_type_name, task_instance.implement.implement_name)
        tasks.append(task)

        print(
            task.time,
            task.machine,
            task.region,
            task.driver,
            task.work,
            task.implement,
            sep="\n",
        )