import os
import sys
from pathlib import Path
from string import Template
from typing import Union
from zoneinfo import ZoneInfo

import loguru

tz = ZoneInfo("Asia/Shanghai")
loguru.logger.configure(patcher=lambda record: record.update(time=record["time"].astimezone(tz)))


class LoguruLogger:
    time = "<green>{time:YYYY-MM-DD HH:mm:ss}</green>"
    level = "<level>{level: <8}</level>"
    name = "<cyan>{name}</cyan>"
    func = "<cyan>{function}</cyan>"
    line = "<cyan>{line}</cyan>"
    message = "<level>{message}</level>"
    exception = "<red>{exception}</red>"

    def __init__(
            self,
            level: str = "INFO",
            log_dir: Union[str, Path] = None,
            log_file: str = 'access.log',
            std_output: bool = True,
            file_output: bool = True,
            **kwargs
    ):
        self.level = level
        self.log_path = self._get_log_path(log_dir, log_file)
        self.std_output = std_output
        self.file_output = file_output
        self.logger = self.get_logger(**kwargs)

    @staticmethod
    def _get_log_path(log_dir, log_file):
        log_dir = log_dir if log_dir else os.path.expanduser("~")
        log_dir = Path(log_dir) if isinstance(log_dir, str) else log_dir
        log_path = log_dir.joinpath(log_file)
        return log_path

    @property
    def template(self) -> Template:
        return Template(
            "$time $c $level $c $name:$func:$line $c PID: $pid $c - $message$extra \n$exception\n"
        )

    def message_format(self, record):
        extra: dict = record['extra']
        extras = []
        for k, v in extra.items():
            extras.append(f'{k}: {v}')
        extras = f" - <blue>{' - '.join(extras)}</blue>" if extras else ""
        pid = f"<green>{record['process'].id}</green>"

        log_format = self.template.substitute(
            c='<red>|</red>', time=self.time, level=self.level,
            name=self.name, func=self.func, line=self.line,
            pid=pid, message=self.message, extra=extras,
            exception=self.exception
        )
        return log_format

    def get_logger(self, **kwargs):
        rotation = kwargs.get("rotation", "00:00")
        retention = kwargs.get("retention", "7 days")
        enqueue = kwargs.get("enqueue", True)
        compression = kwargs.get("compression", "zip")
        encoding = kwargs.get("encoding", "utf-8")

        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        loguru.logger.remove()
        if self.std_output:
            loguru.logger.add(sys.stdout, format=self.message_format, level=self.level)

        if self.file_output:
            loguru.logger.add(
                self.log_path, format=self.message_format, rotation=rotation,
                retention=retention, enqueue=enqueue, compression=compression, encoding=encoding
            )
        return loguru.logger
