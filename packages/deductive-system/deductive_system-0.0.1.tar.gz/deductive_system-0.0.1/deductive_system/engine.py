from __future__ import annotations
import typing
import enum
import dataclasses
import pyparsing


class TermTypeError(Exception):
    pass


class TermParseError(Exception):
    pass


class TermUnificationError(Exception):
    pass


class RuleDeductionError(Exception):
    pass


class RuleParseError(Exception):
    pass


@dataclasses.dataclass(frozen=True)
class Variable:
    name: str

    def __str__(self) -> str:
        return "'" + self.name


@dataclasses.dataclass(frozen=True)
class Item:
    name: str

    def __str__(self) -> str:
        return self.name


@dataclasses.dataclass(frozen=True)
class Term:
    term: Variable | Item | tuple[Term, ...]

    def __str__(self) -> str:
        match self.term:
            case Variable():
                return str(self.term)
            case Item():
                return str(self.term)
            case tuple():
                return "(" + " ".join(str(term) for term in self.term) + ")"

    @property
    def variable(self) -> Variable:
        if isinstance(self.term, Variable):
            return self.term
        raise TermTypeError("Term is not a variable")

    @property
    def item(self) -> Item:
        if isinstance(self.term, Item):
            return self.term
        raise TermTypeError("Term is not an item")

    def __len__(self) -> int:
        if isinstance(self.term, tuple):
            return len(self.term)
        raise TermTypeError("Term is not a tuple")

    def __getitem__(self, index: int) -> Term:
        if isinstance(self.term, tuple):
            return self.term[index]
        raise TermTypeError("Term is not a tuple")

    def __iter__(self) -> typing.Iterator[Term]:
        if isinstance(self.term, tuple):
            yield from self.term
            return
        raise TermTypeError("Term is not a tuple")

    def find_variables(self) -> typing.Iterator[Variable]:
        match self.term:
            case Variable():
                yield self.term
            case Item():
                pass
            case tuple():
                for term in self.term:
                    yield from term.find_variables()

    def ground(self, dictionary: dict[Variable, Term]) -> Term:
        match self.term:
            case Variable():
                return dictionary.get(self.term, self)
            case Item():
                return self
            case tuple():
                return Term(tuple(term.ground(dictionary) for term in self.term))

    def size(self) -> int:
        match self.term:
            case Variable():
                return 1
            case Item():
                return 1
            case tuple():
                return sum(term.size() for term in self.term)

    @classmethod
    def _prepare_parser(cls) -> typing.Any:
        charset = pyparsing.pyparsing_unicode.printables
        exclude = "'()"
        for char in exclude:
            charset = charset.replace(char, "")
        item = pyparsing.Word(charset).setParseAction(lambda x: Item(x[0]))
        variable = (pyparsing.Suppress("'") + item).setParseAction(lambda x: Variable(x[0].name))
        term = pyparsing.Forward()
        _list = (pyparsing.Suppress("(") + pyparsing.Group(pyparsing.OneOrMore(term)) + pyparsing.Suppress(")")).setParseAction(lambda x: tuple(x[0]))
        term <<= (item | variable | _list).setParseAction(lambda x: Term(x[0]))
        return term

    _term: typing.Any = dataclasses.field(default=None, init=False, repr=False, hash=False, compare=False)

    @classmethod
    def _syntax_parse(cls, text: str) -> Term:
        if cls._term is None:
            cls._term = cls._prepare_parser()
        result = cls._term.parseString(text)[0]
        return result

    @classmethod
    def parse(cls, value: typing.Any) -> Term:
        if isinstance(value, Term):
            return value
        if isinstance(value, Variable):
            return Term(value)
        if isinstance(value, Item):
            return Term(value)
        if isinstance(value, tuple):
            return Term(tuple(cls.parse(term) for term in value))
        if isinstance(value, list):
            return Term(tuple(cls.parse(term) for term in value))
        if isinstance(value, str):
            return cls._syntax_parse(value)
        raise TermParseError("Cannot parse value to Term")

    def __matmul__(self, other: Term) -> tuple[dict[Variable, Term], dict[Variable, Term]]:
        match self.term, other.term:
            case Variable(), Variable():
                if self.variable == other.variable:
                    return {}, {}
                else:
                    return {self.variable: other}, {}
            case Item(), Item():
                if self.item == other.item:
                    return {}, {}
                raise TermUnificationError("Cannot unify items")
            case tuple(), tuple():
                if len(self) != len(other):
                    raise TermUnificationError("Cannot unify terms")
                dictionary_self: dict[Variable, Term] = {}
                dictionary_other: dict[Variable, Term] = {}
                for term_self, term_other in zip(self, other):
                    dict_self, dict_other = term_self @ term_other
                    for dict_self_key, dict_self_value in dict_self.items():
                        if dict_self_key in dictionary_self:
                            if dictionary_self[dict_self_key] != dict_self_value:
                                raise TermUnificationError("Cannot unify terms")
                        dictionary_self[dict_self_key] = dict_self_value
                    for dict_other_key, dict_other_value in dict_other.items():
                        if dict_other_key in dictionary_other:
                            if dictionary_other[dict_other_key] != dict_other_value:
                                raise TermUnificationError("Cannot unify terms")
                        dictionary_other[dict_other_key] = dict_other_value
                return dictionary_self, dictionary_other
            case Variable(), _:
                return {self.variable: other}, {}
            case _, Variable():
                return {}, {other.variable: self}
            case _:
                raise TermUnificationError("Cannot unify terms")


V: type[Variable] = Variable
T: typing.Callable[[str], Term] = Term.parse


class RuleType(enum.Enum):
    STATEMENT = 0
    SCHEMA = 1
    REALRULE = 2


@dataclasses.dataclass(frozen=True)
class Rule:
    premises: tuple[Term, ...]
    conclusion: Term

    def execute(self, pool: list[Rule]) -> Rule:
        new_premises = []
        for premise in self.premises:
            for rule in pool:
                if not rule.is_real_rule():
                    if rule.conclusion == premise:
                        break
            else:
                new_premises.append(premise)
        return Rule(tuple(new_premises), self.conclusion)

    def find_variables(self) -> typing.Iterator[Variable]:
        for term in self.premises:
            yield from term.find_variables()
        yield from self.conclusion.find_variables()

    def is_real_rule(self) -> bool:
        return self.premises != ()

    def get_rule_type(self) -> RuleType:
        if self.premises:
            return RuleType.REALRULE
        if any(self.find_variables()):
            return RuleType.SCHEMA
        return RuleType.STATEMENT

    def ground(self, dictionary: dict[Variable, Term]) -> Rule:
        new_premises = tuple(term.ground(dictionary) for term in self.premises)
        new_conclusion = self.conclusion.ground(dictionary)
        return Rule(new_premises, new_conclusion)

    def __matmul__(self, other: Rule) -> Rule:
        if other.is_real_rule() or not self.is_real_rule():
            raise RuleDeductionError("Cannot apply deduction")
        dictionary_self, dictionary_other = self.premises[0] @ other.conclusion
        candidate_self = self.ground(dictionary_self)
        candidate_other = other.ground(dictionary_other)
        if candidate_self.premises[0] == candidate_other.conclusion:
            return Rule(
                tuple(candidate_self.premises[1:]),
                candidate_self.conclusion,
            )
        raise RuleDeductionError("Cannot apply deduction")

    def size(self) -> int:
        return sum(premise.size() for premise in self.premises) + self.conclusion.size()

    def __str__(self) -> str:
        premise_str = [str(premise) for premise in self.premises]
        conclusion_str = str(self.conclusion)
        max_len = max(*(len(premise) for premise in premise_str), len(conclusion_str), 4)
        return "\n".join(premise_str) + "\n" + "-" * max_len + "\n" + conclusion_str + "\n"


def R(text: str) -> Rule:
    lines = [line for line in text.splitlines() if line.strip() != '']
    conclusion = T(lines[-1])
    premises = tuple(T(line) for line in lines[:-2])
    if len(lines) != 1 and lines[-2].replace("-", "").replace(" ", "") != "":
        raise RuleParseError("Invalid format")
    return Rule(premises, conclusion)


class InterpretationError(Exception):
    pass


class Interpretation():

    def __init__(self) -> None:
        self._symbol_to_world: dict[int, typing.Callable[[Item], typing.Any]] = {}
        self._symbol_to_world_index: int = 0
        self._world_to_symbol: dict[int, typing.Callable[[typing.Any], Item]] = {}
        self._world_to_symbol_index: int = 0

    def register_symbol_to_world(self, func: typing.Callable[[Item], typing.Any]) -> int:
        self._symbol_to_world_index += 1
        self._symbol_to_world[self._symbol_to_world_index] = func
        return self._symbol_to_world_index

    def unregister_symbol_to_world(self, index: int) -> None:
        if index in self._symbol_to_world:
            del self._symbol_to_world[index]

    def register_world_to_symbol(self, func: typing.Callable[[typing.Any], Item]) -> int:
        self._world_to_symbol_index += 1
        self._world_to_symbol[self._world_to_symbol_index] = func
        return self._world_to_symbol_index

    def unregister_world_to_symbol(self, index: int) -> None:
        if index in self._world_to_symbol:
            del self._world_to_symbol[index]

    def symbol_to_world(self, item: Item) -> typing.Any:
        for func in self._symbol_to_world.values():
            try:
                result = func(item)
                return result
            except InterpretationError:
                continue
        raise InterpretationError("There is no interpretation for this item")

    def world_to_symbol(self, value: typing.Any) -> Item:
        for func in self._world_to_symbol.values():
            try:
                result = func(value)
                return result
            except InterpretationError:
                continue
        raise InterpretationError("There is no interpretation for this value")
