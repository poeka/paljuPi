import abc
import defs


class Context:
    """
    Define the interface of interest to clients.
    Maintain an instance of a State's subclass that defines the
    current state.
    """

    def __init__(self):
        self._state = Off()

    def work(self, pool):
        self._state.handle(self, pool)


class State(metaclass=abc.ABCMeta):
    """
    Define an interface for encapsulating the behavior associated with a
    particular state of the Context.
    """

    @abc.abstractmethod
    def get_name(self):
        pass

    @abc.abstractmethod
    def handle(self, context, pool):
        pass


class On(State):
    """
    Implement a behavior associated with a state of the Context.
    """

    def get_name(self):
        return defs.ON

    def handle(self, context, pool):
        if pool.get_water_level() != -1:
            if pool.get_water_level() < pool.get_water_level_target():
                pool.open_valve()

            elif pool.get_water_level() >= pool.get_water_level_target():
                pool.close_valve()

        if pool.floatSwitch.get_state() == 0:
            if pool.get_state() != defs.FOFF:
                pool.set_state(defs.FOFF)
                context.state = Foff()
                return

            else:
                pool.set_state(defs.OFF)
                context.state = Off()
                return

        elif pool.floatSwitch.get_state() == 1:
            if pool.get_state() == defs.FOFF:
                context.state = Foff()
                return

            elif pool.get_state() == defs.ON:
                if pool.get_temp_high() < pool.get_target():
                    pool.set_state(defs.ON)
                    return

                elif pool.get_temp_high() >= pool.get_target():
                    pool.set_state(defs.UPKEEP)
                    context.state = Upkeep()
                    return

            elif pool.get_state() == defs.UPKEEP:
                if pool.get_temp_high() <= pool.get_lower_limit():
                    pool.set_state(defs.ON)
                    return

            # HERE

            elif pool.get_state() == defs.OFF:

                if pool.get_temp_high() <= pool.get_lower_limit():
                    pool.set_state(defs.FOFF)
                    return


class Off(State):
    """
    Implement a behavior associated with a state of the Context.
    """

    def get_name(self):
        return defs.OFF

    def handle(self, pool):
        pass


class Upkeep(State):
    """
    Implement a behavior associated with a state of the Context.
    """

    def get_name(self):
        return defs.UPKEEP

    def handle(self, pool):
        pass


class Foff(State):
    """
    Implement a behavior associated with a state of the Context.
    """

    def get_name(self):
        return defs.FOFF

    def handle(self, pool):
        pass
