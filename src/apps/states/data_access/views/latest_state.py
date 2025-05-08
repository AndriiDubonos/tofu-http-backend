from domain_model.unit_of_work.unit_of_work import UnitOfWork


class View:
    def __init__(self, unit_of_work: UnitOfWork):
        self._unit_of_work = unit_of_work
