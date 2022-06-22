from typing import TYPE_CHECKING, Tuple

from pyteal.ir import TealBlock, TealSimpleBlock, TealOp, Op
from pyteal.ast.expr import Expr

if TYPE_CHECKING:
    from pyteal.compiler import CompileOptions


class Comment(Expr):
    def __init__(self, expr: Expr, comment: str):
        self.expr = expr
        self.comment = " ".join(
            [i.strip() for i in comment.split("\n") if not (i.isspace() or len(i) == 0)]
        )

    def __teal__(self, options: "CompileOptions") -> Tuple[TealBlock, TealSimpleBlock]:
        op = TealOp(self, Op.comment, self.comment)
        return TealBlock.FromOp(options, op, self.expr)

    def __str__(self):
        return f"(Comment {self.comment} ({self.expr}))"

    def type_of(self):
        return self.expr.type_of()

    def has_return(self):
        return self.expr.has_return()


Comment.__module__ = "pyteal"
