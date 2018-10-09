from sqlalchemy.orm import Query


class BaseQuery(Query):
    def get(self, ident):
        return Query.get(self.populate_existing(), ident)

    def __iter__(self):
        return Query.__iter__(self.filters())

    def from_self(self, *ent):
        return Query.from_self(self.filters(), *ent)

    def filters(self):
        mzero = self._mapper_zero()
        if mzero is not None:
            if hasattr(mzero.class_, 'deleted'):
                return self.enable_assertions(False).filter(
                    mzero.class_.deleted.is_(None)
                )
            return self
        else:
            return self
