from typing import Optional

from aim._sdk.types.run import Run

try:
    from xgboost.callback import TrainingCallback
except ImportError:
    raise RuntimeError(
        'This contrib module requires XGBoost to be installed. '
        'Please install it with command: \n pip install xgboost'
    )


class AimCallback(TrainingCallback):

    def __init__(self, repo: Optional[str] = None,
                 experiment: Optional[str] = None,
                 log_system_params: Optional[bool] = True,
                 ):
        super().__init__()
        self._repo_path = repo
        self._experiment = experiment
        self._log_system_params = log_system_params
        self._run = None
        self._run_hash = None

    @property
    def experiment(self) -> Run:
        if not self._run:
            self.setup()
        return self._run

    def setup(self):
        if self._run:
            return
        if self._run_hash:
            self._run = Run(self._run_hash, repo=self._repo_path)
        else:
            self._run = Run(repo=self._repo_path)
            if self._experiment is not None:
                self._run.experiment = self._experiment
            self._run_hash = self._run.hash
        if self._log_system_params:
            self._run.enable_system_monitoring()

    def before_training(self, model):
        self.setup()
        return model

    def after_iteration(self, model, epoch: int, evals_log) -> bool:
        if not evals_log:
            return False

        for data, metric in evals_log.items():
            for metric_name, log in metric.items():
                stdv: Optional[float] = None
                if isinstance(log[-1], tuple):
                    score = log[-1][0]
                    stdv = log[-1][1]
                else:
                    score = log[-1]

                self._run.track(score, step=0, name=metric_name, context={'stdv': False})
                if stdv is not None:
                    self._run.track(score, step=0, name=metric_name, context={'stdv': True})

        return False

    def after_training(self, model):
        self.close()
        return model

    def close(self):
        if self._run:
            self._run.close()
            del self._run
            self._run = None

    def __del__(self):
        self.close()
