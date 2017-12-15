import sympy
from sympy.assumptions.assume import AppliedPredicate, global_assumptions
from typing import Dict, List, Union

a, b, c = sympy.symbols('a b c')
d_a, d_b, d_c = sympy.symbols('Δa Δb Δc')


class Expression:
    args: List[sympy.Symbol]
    expr: sympy.Expr

    def __init__(self, args: List[sympy.Symbol], expr: sympy.Expr):
        """Initialize an Expression instance with a sympy expression and its arguments.

        :param args: the variables in the expression
        :param expr: the mathematical expression

        >>> Expression([a, b, c], a + b + c)
        f(a, b, c) = a + b + c
        >>> Expression([a, b, c], a * b / c)
        f(a, b, c) = a*b/c
        >>> Expression([a, b, c], sympy.root(a ** b, c))
        f(a, b, c) = (a**b)**(1/c)
        """
        self.args = args
        self.expr = expr

    def __repr__(self) -> str:
        """Show this expression as a mathematical function.

        :rtype str

        >>> str(Expression([a], a * sympy.pi))
        'f(a) = pi*a'
        >>> repr(Expression([], sympy.E))
        'f() = E'
        """
        if len(self.args) == 1:
            return f"f({self.args[0]}) = {self.expr}"
        return f"f{tuple(self.args)} = {self.expr}"

    def evaluate(self, values: Dict[Union[str, sympy.Symbol], float]) -> sympy.Expr:
        """Evaluate the expression with the given values.

        :param values: a dictionary mapping all the sympy symbols in the args to numeric values
        :return: the result of the evaluation as an sympy expression

        >>> Expression([a, b, c], a + b + c).evaluate({a: 1, b: 2, c: 3})
        6
        >>> Expression([a, b, c], a ** b + c).evaluate({'a': c, 'b': 1})
        2*c
        """
        return self.expr.subs(values)

    def calculate_absolute_uncertainty(self, *assumptions: AppliedPredicate) -> 'Expression':
        """Calculate the absolute uncertainty in the expression, assuming all args given are independent.

        :return: the absolute uncertainty of this expression
        :rtype: Expression

        >>> Expression([a], c * a).calculate_absolute_uncertainty(sympy.Q.positive(c))
        f(Δa) = c*Δa
        >>> Expression([a, b, c], a + b - c).calculate_absolute_uncertainty()
        f(Δa, Δb, Δc) = Δa + Δb + Δc
        """
        uncertainty_expr = sympy.Integer(0)  # just in case
        uncertainty_args = []
        global_assumptions.add(*assumptions)

        for var in self.args:
            d_var = sympy.symbols('Δ' + var.name)
            uncertainty_args.append(d_var)
            uncertainty_expr += sympy.Abs(self.expr.diff(var)) * d_var
            global_assumptions.add(sympy.Q.positive(var))

        uncertainty_expr = sympy.refine(uncertainty_expr)
        global_assumptions.clear()
        return Expression(uncertainty_args, uncertainty_expr)

    def calculate_fractional_uncertainty(self, *assumptions: AppliedPredicate) -> 'Expression':
        """Calculate the absolute uncertainty in the expression, assuming all args given are independent.

        :return: the fractional uncertainty of this expression
        :rtype: Expression

        >>> Expression([a, b, c], a * b / c).calculate_fractional_uncertainty()
        f(Δa, Δb, Δc) = Δc/c + Δb/b + Δa/a
        >>> Expression([a], a ** b).calculate_fractional_uncertainty(sympy.Q.positive(b))
        f(Δa) = b*Δa/a
        """
        absolute_uncertainty = self.calculate_absolute_uncertainty(*assumptions)
        frac_uncertainty_expr = sympy.Integer(0)
        if type(absolute_uncertainty.expr) == sympy.Add:
            for addend in absolute_uncertainty.expr.args:
                frac_uncertainty_expr += addend / self.expr
        elif type(absolute_uncertainty.expr) == sympy.Mul or type(absolute_uncertainty) == sympy.Pow:
            frac_uncertainty_expr = absolute_uncertainty.expr / self.expr
        else:
            frac_uncertainty_expr = sympy.Mul(absolute_uncertainty.expr, sympy.Pow(self.expr, -1), evaluate=False)
        return Expression(absolute_uncertainty.args, frac_uncertainty_expr)

    def to_latex(self) -> str:
        r"""Get the latex form of this expression.

        :rtype: str

        >>> Expression([a, b, c], a + b + c).to_latex()
        'a + b + c'
        >>> Expression([a, b, c], a * b / c).to_latex()
        '\\frac{a b}{c}'
        >>> Expression([a, b, c], sympy.root(a ** b, c)).to_latex()
        '\\left(a^{b}\\right)^{\\frac{1}{c}}'
        """
        return sympy.latex(self.expr)

    @classmethod
    def from_latex(cls, latex: str) -> 'Expression':
        pass
