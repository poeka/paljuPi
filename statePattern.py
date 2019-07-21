import abc
import defs

# State machine implemented with state pattern


class Context:

    def __init__(self):
        self.state = Off()

    def work(self, pool):
        self.state.handle(self, pool)


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

        if pool.get_next_state() == defs.FOFF:
            pool.set_next_state("")
            pool.set_state(defs.FOFF)
            context.state = Foff()
            return

        if pool.floatSwitch.get_state() == 0:
            pool.set_state(defs.OFF)
            context.state = Off()
            return

        elif pool.floatSwitch.get_state() == 1:
            if pool.get_temp_high() >= pool.get_target():
                pool.set_state(defs.UPKEEP)
                context.state = Upkeep()
                return


class Off(State):

    def get_name(self):
        return defs.OFF

    def handle(self, context, pool):
        pool.handle_valve()

        if pool.get_next_state() == defs.FOFF:
            pool.set_next_state("")
            pool.set_state(defs.FOFF)
            context.state = Foff()
            return

        if pool.floatSwitch.get_state() == 0:
            return

        elif pool.floatSwitch.get_state() == 1:
            pool.set_state(defs.ON)
            context.state = On()
            return


class Upkeep(State):

    def get_name(self):
        return defs.UPKEEP

    def handle(self, context, pool):
        pool.handle_valve()

        if pool.get_next_state() == defs.FOFF:
            pool.set_next_state("")
            pool.set_state(defs.FOFF)
            context.state = Foff()
            return

        if pool.floatSwitch.get_state() == 0:
            pool.set_state(defs.OFF)
            context.state = Off()
            return

        elif pool.floatSwitch.get_state() == 1:
            if pool.get_temp_high() <= pool.get_lower_limit():
                pool.set_state(defs.ON)
                context.state = On()
                return


class Foff(State):

    def get_name(self):
        return defs.FOFF

    def handle(self, context, pool):
        pool.handle_valve()

        if pool.get_next_state() == defs.ON:
            if pool.floatSwitch.get_state() == 1:
                pool.set_next_state("")
                pool.set_state(defs.ON)
                context.state = On()
                return
