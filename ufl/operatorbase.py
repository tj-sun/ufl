"Base class for all operators, i.e. non-terminal expr types."

# Copyright (C) 2008-2014 Martin Sandve Alnes
#
# This file is part of UFL.
#
# UFL is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# UFL is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with UFL. If not, see <http://www.gnu.org/licenses/>.
#
# Modified by Anders Logg, 2008

from six import iteritems

from ufl.expr import Expr
from ufl.log import error
from ufl.core.ufl_type import ufl_type
from ufl.core.index import Index

def _compute_hash(expr): # Best so far
    hashdata = ( (expr.__class__._ufl_class_,)
            + tuple(hash(o) for o in expr.ufl_operands) )
    return hash(str(hashdata))

_hashes = set()
_hashes_added = 0
def compute_hash_with_stats(expr):
    global _hashes, _hashes_added

    h = compute_hash(expr)

    _hashes.add(h)
    _hashes_added += 1
    if _hashes_added % 10000 == 0:
        print("HASHRATIO", len(_hashes)/float(_hashes_added))

    return h

# This seems to be the best of the above
compute_hash = _compute_hash
#compute_hash = compute_hash_with_stats


#--- Base class for operator objects ---

@ufl_type(is_abstract=True, is_terminal=False)
class Operator(Expr):
    __slots__ = ("ufl_operands",)

    def __init__(self, operands=None):
        Expr.__init__(self)

        # If operands is None, the type sets this itself. This is to get around
        # some tricky too-fancy __new__/__init__ design in algebra.py, for now.
        if operands is not None:
            self.ufl_operands = operands

    def reconstruct(self, *operands):
        "Return a new object of the same type with new operands."
        return self.__class__._ufl_class_(*operands)

    def signature_data(self):
        return self._ufl_typecode_

    def _ufl_compute_hash_(self):
        "Compute a hash code for this expression. Used by sets and dicts."
        return compute_hash(self)

    def is_cellwise_constant(self):
        "Return whether this expression is spatially constant over each cell."
        return all(o.is_cellwise_constant() for o in self.ufl_operands)

    # --- Transitional property getters, to be implemented directly in all classes ---

    def operands(self):
        return self.ufl_operands

    def free_indices(self):
        "Intermediate helper property getter to transition from .free_indices() to .ufl_free_indices."
        return tuple(Index(count=i) for i in self.ufl_free_indices)

    def index_dimensions(self):
        "Intermediate helper property getter to transition from .index_dimensions() to .ufl_index_dimensions."
        return { Index(count=i): d for i, d in zip(self.ufl_free_indices, self.ufl_index_dimensions) }
