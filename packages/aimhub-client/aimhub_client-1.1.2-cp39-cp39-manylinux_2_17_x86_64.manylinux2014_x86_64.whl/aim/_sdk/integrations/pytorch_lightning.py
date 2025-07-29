import os
import importlib.util
from typing import Any, Dict, Optional, Union
from argparse import Namespace

import packaging.version

if importlib.util.find_spec("lightning"):
    import lightning.pytorch as pl

    from lightning.pytorch.loggers.logger import (
        Logger, rank_zero_experiment
    )

    from lightning.pytorch.utilities import rank_zero_only
elif importlib.util.find_spec("pytorch_lightning"):
    import pytorch_lightning as pl

    if packaging.version.parse(pl.__version__) < packaging.version.parse("1.7"):
        from pytorch_lightning.loggers.base import (
            LightningLoggerBase as Logger,
            rank_zero_experiment,
        )
    else:
        from pytorch_lightning.loggers.logger import (
            Logger,
            rank_zero_experiment,
        )

    from pytorch_lightning.utilities import rank_zero_only
else:
    raise RuntimeError(
        'This contrib module requires PyTorch Lightning to be installed. '
        'Please install it with command: \n pip install pytorch-lightning'
        'or \n pip install lightning'
    )

from aim._sdk.types.run import Run


class AimLogger(Logger):
    def __init__(self,
                 repo: Optional[str] = None,
                 experiment: Optional[str] = None,
                 train_metric_prefix: Optional[str] = 'train_',
                 val_metric_prefix: Optional[str] = 'val_',
                 test_metric_prefix: Optional[str] = 'test_',
                 log_system_params: Optional[bool] = True,
                 run_name: Optional[str] = None,
                 run_hash: Optional[str] = None,
                 ):
        super().__init__()

        self._experiment_name = experiment
        self._run_name = run_name
        self._repo_path = repo

        self._train_metric_prefix = train_metric_prefix
        self._val_metric_prefix = val_metric_prefix
        self._test_metric_prefix = test_metric_prefix
        self._log_system_params = log_system_params

        self._run = None
        self._run_hash = run_hash

    @staticmethod
    def _convert_params(params: Union[Dict[str, Any], Namespace]) -> Dict[str, Any]:
        # in case converting from namespace
        if isinstance(params, Namespace):
            params = vars(params)

        if params is None:
            params = {}

        return params

    @property
    @rank_zero_experiment
    def experiment(self) -> Run:
        if self._run is None:
            if self._run_hash:
                self._run = Run(self._run_hash, repo=self._repo_path)
                if self._run_name is not None:
                    self._run.name = self._run_name
            else:
                self._run = Run(repo=self._repo_path)
                if self._experiment_name is not None:
                    self._run.experiment = self._experiment_name
                self._run_hash = self._run.hash
            if self._log_system_params:
                self._run.enable_system_monitoring()
        return self._run

    @rank_zero_only
    def log_hyperparams(self, params: Union[Dict[str, Any], Namespace]):
        params = self._convert_params(params)

        # Handle OmegaConf object
        try:
            from omegaconf import OmegaConf
        except ModuleNotFoundError:
            pass
        else:
            # Convert to primitives
            if OmegaConf.is_config(params):
                params = OmegaConf.to_container(params, resolve=True)

        for key, value in params.items():
            self.experiment.set(('hparams', key), value, strict=False)

    @rank_zero_only
    def log_metrics(self, metrics: Dict[str, float],
                    step: Optional[int] = None):
        assert rank_zero_only.rank == 0, \
            'experiment tried to log from global_rank != 0'

        metric_items: Dict[str: Any] = {k: v for k, v in metrics.items()}

        if 'epoch' in metric_items:
            epoch: int = metric_items.pop('epoch')
        else:
            epoch = None

        for k, v in metric_items.items():
            name = k
            context = {}
            if self._train_metric_prefix \
                    and name.startswith(self._train_metric_prefix):
                name = name[len(self._train_metric_prefix):]
                context['subset'] = 'train'
            elif self._test_metric_prefix \
                    and name.startswith(self._test_metric_prefix):
                name = name[len(self._test_metric_prefix):]
                context['subset'] = 'test'
            elif self._val_metric_prefix \
                    and name.startswith(self._val_metric_prefix):
                name = name[len(self._val_metric_prefix):]
                context['subset'] = 'val'
            self.experiment.track(v, name=name, step=step, epoch=epoch, context=context)

    @rank_zero_only
    def finalize(self, status: str = '') -> None:
        super().finalize(status)
        if self._run:
            self._run.close()
            del self._run
            self._run = None

    def __del__(self):
        self.finalize()


    @property
    def name(self) -> str:
        return self._experiment_name

    @property
    def version(self) -> str:
        return self.experiment.hash
