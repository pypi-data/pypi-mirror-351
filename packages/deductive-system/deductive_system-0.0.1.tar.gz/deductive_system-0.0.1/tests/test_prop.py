from deductive_system.engine import R, TermUnificationError, RuleDeductionError
from deductive_system.data.prop import mp, axiom1, axiom2, axiom3


def __main__():
    premise = R("(! (! P))")
    target = R("P")

    new_rules = [mp]
    new_facts = [axiom1, axiom2, axiom3, premise]
    old_rules = []
    old_facts = []

    while True:
        rules = []
        facts = []
        for rule in new_rules:
            for fact in new_facts:
                if rule in old_rules and fact in old_facts:
                    continue
                try:
                    result = rule @ fact
                except (TermUnificationError, RuleDeductionError):
                    continue
                if result.size() > 8:
                    continue
                if result.is_real_rule():
                    if result not in new_rules and result not in rules:
                        rules.append(result)
                else:
                    if result not in new_facts and result not in facts:
                        facts.append(result)
                        if result == target:
                            print("Target Found", result)
                            return
        old_rules = new_rules.copy()
        old_facts = new_facts.copy()
        new_rules.extend(rules)
        new_facts.extend(facts)


if __name__ == "__main__":
    __main__()
