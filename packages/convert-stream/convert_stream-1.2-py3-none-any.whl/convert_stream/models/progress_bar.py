#!/usr/bin/env python3

from abc import ABC, abstractmethod
from typing import Optional
from tqdm import tqdm


class ABCProgressBar(ABC):
    """
        Barra de progresso Abstrata
    """

    def __init__(self):
        super().__init__()
        self._num_progress: float = 0
        self.pbar_real: object = None

    @property
    def num_progress(self) -> float:
        return self._num_progress

    @num_progress.setter
    def num_progress(self, new: float):
        if isinstance(new, float):
            self._num_progress = new
            return
        try:
            _prog = float(new)
        except Exception as e:
            print(e)
        else:
            self._num_progress = _prog

    @abstractmethod
    def set_percent(self, percent: float):
        """Seta o progresso com float de porcentagem, ex: '42.8'"""
        pass

    @abstractmethod
    def set_text(self, text: str):
        """Seta um texto indicando a situação atual"""
        pass

    def start(self):
        """Inicia a barra de progresso (pode ser vazio dependendo da implementação)"""
        pass

    def stop(self):
        """Para a barra de progresso (pode ser vazio dependendo da implementação)"""
        pass


class ProgressBarSimple(ABCProgressBar):
    """Barra de progresso simples para mostrar no terminal."""

    def __init__(self, simple_pbar=None):
        super().__init__()
        self.pbar_real = simple_pbar
        self._text: str = 'Aguarde!'

    def set_percent(self, percent):
        if not isinstance(percent, float):
            return
        if len(f'{percent}') > 4:
            percent = round(float(percent), 2)
        self.num_progress = percent
        print(f'[{self.num_progress}%] {self._text} ', end='\r')

    def set_text(self, text: str):
        self._text = text
        print(f'{self._text}', end='\r')

    def start(self):
        pass

    def stop(self):
        pass


class ProgressBarTqdm(ABCProgressBar):
    def __init__(self, tqdm_bar: tqdm):
        super().__init__()
        self.pbar_real = tqdm_bar
        self.total = tqdm_bar.total or 100
        self.last_percent = 0

    def set_percent(self, percent):
        if not isinstance(percent, float):
            return
        if len(f'{percent}') > 4:
            percent = round(float(percent), 2)
        self.num_progress = percent

        try:
            percent = int(percent)
            percent = max(0, min(100, percent))  # Clamp entre 0 e 100
            new_value = int((percent / 100) * self.total)
            delta = new_value - self.pbar_real.n
            if delta > 0:
                self.pbar_real.update(delta)
                self.last_percent = percent
        except ValueError:
            pass  # Ignore valores inválidos
        else:
            pass

    def set_text(self, text: str):
        self.pbar_real.set_description_str(text)

    def set_units(self, unit: Optional[str] = None, unit_scale: Optional[bool] = None,
                  unit_divisor: Optional[int] = None):
        if unit is not None:
            self.pbar_real.unit = unit
        if unit_scale is not None:
            self.pbar_real.unit_scale = unit_scale
        if unit_divisor is not None:
            self.pbar_real.unit_divisor = unit_divisor

    def start(self):
        self.pbar_real.reset(total=self.total)
        self.last_percent = 0

    def stop(self):
        self.pbar_real.close()


class ProgressBarAdapter(object):
    def __init__(self, progress_bar: ABCProgressBar):
        self.pbar_implement: ABCProgressBar = progress_bar

    def get_current_percent(self) -> float:
        return self.pbar_implement.num_progress

    def update_text(self, text: str = ""):
        self.pbar_implement.set_text(text)

    def update_percent(self, percent: float = 0):
        if not isinstance(percent, float):
            try:
                percent = float(percent)
            except Exception as e:
                print(f'{__class__.__name__} {e}')
                percent = 0
        self.pbar_implement.set_percent(percent)

    def update(self, percent: float, status: str = ""):
        self.update_percent(percent)
        if status:
            self.pbar_implement.set_text(status)

    def start(self):
        self.pbar_implement.start()

    def stop(self):
        self.pbar_implement.stop()

