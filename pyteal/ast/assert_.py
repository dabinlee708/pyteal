from typing import TYPE_CHECKING

from pyteal.types import TealType, require_type
from pyteal.ir import TealOp, Op, TealBlock, TealSimpleBlock, TealConditionalBlock
from pyteal.ast.expr import Expr
from pyteal.ast.seq import Seq

if TYPE_CHECKING:
    from pyteal.compiler import CompileOptions


class Assert(Expr):
    """A control flow expression to verify that a condition is true."""

    def __init__(self, cond: Expr, *additional_conds: Expr) -> None:
        """Create an assert statement that raises an error if the condition is false.

        Args:
            cond: The condition to check. Must evaluate to a uint64.
            *additional_conds: Additional conditions to check. Must evaluate to uint64.
        """
        super().__init__()
        require_type(cond, TealType.uint64)
        for cond_single in additional_conds:
            require_type(cond_single, TealType.uint64)
        self.cond = [cond] + list(additional_conds)

    def __teal__(self, options: "CompileOptions"):
        if len(self.cond) > 1:
            asserts = [Assert(cond) for cond in self.cond]
            return Seq(*asserts).__teal__(options)

        if options.version >= Op.assert_.min_version:
            # use assert op if available
            return TealBlock.FromOp(
                options, TealOp(self, Op.assert_), self.cond[0], trace=self.trace
            )


        # if assert op is not available, use branches and err
        condStart, condEnd = self.cond[0].__teal__(options)

        end = TealSimpleBlock([])
        errBlock = TealSimpleBlock([TealOp(self, Op.err)])

        branchBlock = TealConditionalBlock([])
        branchBlock.setTrueBlock(end)
        branchBlock.setFalseBlock(errBlock)

        condEnd.setNextBlock(branchBlock)

        return condStart, end

    def __str__(self):
        return "(Assert {})".format(self.cond)

    def type_of(self):
        return TealType.none

    def has_return(self):
        return False


Assert.__module__ = "pyteal"
