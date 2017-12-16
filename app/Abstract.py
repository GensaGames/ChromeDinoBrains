from abc import ABCMeta, abstractmethod


class OnLearnerCallback:
    __metaclass__ = ABCMeta

    def __init__(self, on_action_callback):
        self.on_action_callback = on_action_callback

    @abstractmethod
    def on_load_source(self, source):
        pass

    @abstractmethod
    def on_get_source(self):
        pass

    @abstractmethod
    def on_start(self):
        pass

    @abstractmethod
    def on_receive(self, params):
        pass


class OnActionCallback:
    __metaclass__ = ABCMeta

    @abstractmethod
    def on_action(self, value):
        pass