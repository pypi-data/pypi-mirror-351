from rich.progress import (
    Progress, 
    SpinnerColumn, 
    TextColumn, 
    BarColumn, 
    TimeElapsedColumn, 
    TimeRemainingColumn
)
from dataclasses import dataclass

MY_FAVORITE_COLORS = ["green", "cyan", "yellow", "magenta", "pink3", "sky_blue3"]

@dataclass
class SimpleTask:
    desc: str
    total: int
    color: str = "auto"
    name: str | None = None
    
    def __post_init__(self):
        if self.name is None:
            self.name = self.desc
            
@dataclass
class SimpleColumn:
    desc: str
    name: str | None = None
    init_value: int = 0
    color: str = "auto"
    
    def __post_init__(self):
        if self.name is None:
            self.name = self.desc

class simple_pbar:
    def __init__(self, 
                 *tasks: SimpleTask,
                 columns: list[SimpleColumn] = [],
                 add_spinner: bool = True,
                 add_percentage: bool = True,
                 add_completed: bool = True,
                 add_time_elapsed: bool = True,
                 add_time_remaining: bool = True):
        self.tasks = tasks
        self.columns = columns
        standard_columns = []
        if add_spinner:
            standard_columns.append(SpinnerColumn())
        standard_columns.append(TextColumn("[progress.description]{task.description}"))
        standard_columns.append(BarColumn())
        if add_percentage:
            standard_columns.append(TextColumn("[progress.percentage]{task.percentage:>3.0f}%"))
        if add_completed:
            standard_columns.append(TextColumn("[progress.completed]{task.completed}/{task.total}"))
        if add_time_elapsed:
            standard_columns.append(TimeElapsedColumn())
        if add_time_remaining:
            standard_columns.append(TimeRemainingColumn())
        color_idx = 0
        for column in self.columns:
            if column.color == "auto":
                column_color = MY_FAVORITE_COLORS[color_idx % len(MY_FAVORITE_COLORS)]
                color_idx += 1
            else:
                column_color = column.color
            standard_columns.append(TextColumn(f"[{column_color}]{column.desc}: {{task.fields[{column.name}]}}[/]"))
        self.progress = Progress(*standard_columns)
        self.task_ids = {}
        
    def __enter__(self):
        self.progress.start()
        color_idx = 0
        
        for task in self.tasks:
            if task.color == "auto":
                task_color = MY_FAVORITE_COLORS[color_idx % len(MY_FAVORITE_COLORS)]
                color_idx += 1
            else:
                task_color = task.color
            self.task_ids[task.name] = self.progress.add_task(
                f"[{task_color}]{task.desc}[/]", 
                total=task.total, 
                **{column.name: column.init_value for column in self.columns})
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.progress.stop()
        
    def go(self, name=None, advance=1, total=None, completed=None):
        if name is None:
            for task in self.tasks:
                self.progress.update(self.task_ids[task.name], advance=advance, completed=completed, total=total)
        else:
            self.progress.update(self.task_ids[name], advance=advance, completed=completed, total=total)
            
    def update_column(self, name=None, column_name=None, value=None):
        if name is None:
            for task in self.tasks:
                self.progress.update(self.task_ids[task.name], **{column_name: value})
        else:
            self.progress.update(self.task_ids[name], **{column_name: value})
        self.progress.refresh()
            
    def reset(self, name=None):
        if name is None:
            for task in self.tasks:
                self.progress.reset(self.task_ids[task.name])
        else:
            self.progress.reset(self.task_ids[name])
        
    def print(self, *args, **kwargs):
        self.progress.print(*args, **kwargs)
        
    def log(self, *args, **kwargs):
        self.progress.log(*args, **kwargs)