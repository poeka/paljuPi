import abc
import defs

# State machine implemented with state pattern


class Context:

    def __init__(self):
        self._state = Off()

    def set_state(self, state):
        self._state = state

    def work(self, pool):
        self._state.handle(self, pool)


class State(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def get_name(self):
        pass

    @abc.abstractmethod
    def handle(self, context, pool):
        pass


class On(State):

    def get_name(self):
        return defs.ON

    def handle(self, context, pool):
        pool.handle_valve()
        pool.start_filter_pump():

        if pool.get_next_state() == defs.FOFF:
            pool.set_next_state("")
            pool.set_state(defs.FOFF)
            context.set_state(Foff())
            return

        if not pool.safe_to_start_burner():
            pool.set_state(defs.OFF)
            context.set_state(Off())
            return

        else:
            if pool.get_temp_high() >= pool.get_target():
                pool.set_state(defs.UPKEEP)
                context.set_state(Upkeep())
                return


class Off(State):

    def get_name(self):
        return defs.OFF

    def handle(self, context, pool):
        pool.handle_valve()

        if pool.get_next_state() == defs.FOFF:
            pool.set_next_state("")
            pool.set_state(defs.FOFF)
            context.set_state(Foff())
            return

        elif pool.safe_to_start_burner():
            pool.set_state(defs.ON)
            context.set_state(On())
            return


class Upkeep(State):

    def get_name(self):
        return defs.UPKEEP

    def handle(self, context, pool):
        pool.handle_valve()

        if pool.get_next_state() == defs.FOFF:
            pool.set_next_state("")
            pool.set_state(defs.FOFF)
            context.set_state(Foff())
            return

        if not pool.safe_to_start_burner():
            pool.set_state(defs.OFF)
            context.set_state(Off())
            return

        else:
            if pool.get_temp_high() <= pool.get_lower_limit():
                pool.set_state(defs.ON)
                context.set_state(On())
                return


class Foff(State):

    def get_name(self):
        return defs.FOFF

    def handle(self, context, pool):
        pool.handle_valve()

        if pool.get_next_state() == defs.ON:
            if pool.safe_to_start_burner():
                pool.set_next_state("")
                pool.set_state(defs.ON)
                context.set_state(On())
                return
            else:
                pool.set_next_state("")
                pool.set_state(defs.OFF)
                context.set_state(Off())
