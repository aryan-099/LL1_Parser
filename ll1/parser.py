import tkinter as tk
from tkinter import messagebox, scrolledtext

# ---------------- PARSER CORE --------------------
# ------------------- LL(1) PARSER -------------------

# Global variables
rules = []
nonterm_userdef = []
term_userdef = []
diction = {}
firsts = {}
follows = {}
start_symbol = ''

# ------------------ Utility Functions ------------------

def removeLeftRecursion(rulesDiction):
    print("\nRemoving Left Recursion...")
    # Handle indirect left recursion by ordering nonterminals
    nonterms = list(rulesDiction.keys())
    newRules = dict(rulesDiction)  # copy to avoid modifying during iteration

    # Step 1: Remove indirect left recursion
    for i in range(len(nonterms)):
        Ai = nonterms[i]
        for j in range(i):
            Aj = nonterms[j]
            new_rhs = []
            for rhs in newRules[Ai]:
                if rhs[0] == Aj:
                    # Replace Aj with its productions
                    for gamma in newRules[Aj]:
                        new_rhs.append(gamma + rhs[1:])
                else:
                    new_rhs.append(rhs)
            newRules[Ai] = new_rhs

        # Step 2: Remove direct left recursion for Ai
        alphaRules = []
        betaRules = []
        for rhs in newRules[Ai]:
            if rhs[0] == Ai:
                alphaRules.append(rhs[1:])
            else:
                betaRules.append(rhs)

        if alphaRules:
            Ai_prime = Ai + "'"
            while Ai_prime in newRules or Ai_prime in rulesDiction:
                Ai_prime += "'"
            newBetaRules = [beta + [Ai_prime] for beta in betaRules]
            newAlphaRules = [alpha + [Ai_prime] for alpha in alphaRules]
            newAlphaRules.append(['#'])  # epsilon

            newRules[Ai] = newBetaRules
            newRules[Ai_prime] = newAlphaRules
            print(f"Left recursion found in {Ai}. Created new productions for {Ai_prime}")

    print("Grammar after Left Recursion removal:")
    for k, v in newRules.items():
        rhs_str = [" ".join(x) for x in v]
        print(f"{k} -> {' | '.join(rhs_str)}")
    return newRules


def LeftFactoring(rulesDiction):
    print("\nPerforming Left Factoring...")
    newDict = {}
    for lhs in rulesDiction:
        allrhs = rulesDiction[lhs]
        prefix_map = {}
        for rhs in allrhs:
            if len(rhs) == 0:
                continue
            prefix = rhs[0]
            prefix_map.setdefault(prefix, []).append(rhs)

        new_rules = []
        temp_new = {}

        for prefix, rhss in prefix_map.items():
            if len(rhss) > 1:
                lhs_prime = lhs + "'"
                while lhs_prime in rulesDiction or lhs_prime in temp_new or lhs_prime in newDict:
                    lhs_prime += "'"
                # New rule for lhs
                new_rules.append([prefix, lhs_prime])
                # Rules for lhs_prime
                ex_rules = [r[1:] if len(r) > 1 else ['#'] for r in rhss]
                temp_new[lhs_prime] = ex_rules
                print(f"Left factoring applied on {lhs}, created {lhs_prime}")
            else:
                new_rules.append(rhss[0])

        newDict[lhs] = new_rules
        for k, v in temp_new.items():
            newDict[k] = v

    print("Grammar after Left Factoring:")
    for k, v in newDict.items():
        rhs_str = [" ".join(x) for x in v]
        print(f"{k} -> {' | '.join(rhs_str)}")
    return newDict


def first(rule, visited=None):
    global diction, term_userdef
    if visited is None:
        visited = set()

    if len(rule) == 0:
        return []

    first_symbol = rule[0]

    # Terminal case
    if first_symbol in term_userdef:
        return [first_symbol]

    # Epsilon
    if first_symbol == '#':
        return ['#']

    # Nonterminal
    if first_symbol in diction:
        if first_symbol in visited:
            return []  # Prevent infinite recursion

        visited.add(first_symbol)
        fres = []
        for rhs in diction[first_symbol]:
            res = first(rhs, visited.copy())
            fres.extend(res)
        fres = list(set(fres))

        if '#' in fres:
            fres.remove('#')
            if len(rule) > 1:
                fres.extend(first(rule[1:], visited.copy()))
            else:
                fres.append('#')
        return list(set(fres))

    return []


def follow(nt, visited=None):
    global start_symbol, diction
    if visited is None:
        visited = set()

    if nt in visited:
        return []

    visited.add(nt)
    solset = set()

    if nt == start_symbol:
        solset.add('$')

    for curNT in diction:
        rhs = diction[curNT]
        for subrule in rhs:
            for i in range(len(subrule)):
                if subrule[i] == nt:
                    follow_part = subrule[i+1:]
                    if follow_part:
                        res = first(follow_part)
                        for r in res:
                            if r != '#':
                                solset.add(r)
                        if '#' in res:
                            if curNT != nt:
                                solset.update(follow(curNT, visited.copy()))
                    else:
                        if curNT != nt:
                            solset.update(follow(curNT, visited.copy()))
    return list(solset)
# ------------------ FIRST & FOLLOW ------------------
def computeAllFirsts():
    global rules, diction, firsts
    
    # Parse grammar rules into dictionary form
    for rule in rules:
        lhs, rhs = rule.split("->")
        lhs = lhs.strip()
        rhs = rhs.strip()
        alternatives = rhs.split('|')
        diction[lhs] = [alt.strip().split() for alt in alternatives]

    print("\nOriginal Grammar:")
    for k, v in diction.items():
        rhs_str = [" ".join(x) for x in v]
        print(f"{k} -> {' | '.join(rhs_str)}")

    # Apply left recursion removal and left factoring (assumed to be implemented)
    diction.update(removeLeftRecursion(diction))
    diction.update(LeftFactoring(diction))

    # Initialize first sets as empty sets
    firsts.clear()
    for nonterm in diction.keys():
        firsts[nonterm] = set()

    # Repeat until no change
    changed = True
    while changed:
        changed = False
        for nonterm, productions in diction.items():
            for prod in productions:
                # Compute FIRST for this production
                i = 0
                add_epsilon = True
                while i < len(prod) and add_epsilon:
                    symbol = prod[i]

                    if symbol not in diction:  # terminal
                        if symbol not in firsts[nonterm]:
                            firsts[nonterm].add(symbol)
                            changed = True
                        add_epsilon = False
                    else:  # non-terminal
                        before = len(firsts[nonterm])
                        # Add FIRST(symbol) except epsilon
                        firsts[nonterm].update(firsts[symbol] - set('#'))
                        after = len(firsts[nonterm])
                        if after > before:
                            changed = True

                        if '#' in firsts[symbol]:
                            i += 1  # check next symbol for epsilon
                        else:
                            add_epsilon = False

                else:
                    # If all symbols have epsilon, add epsilon to FIRST(nonterm)
                    if add_epsilon:
                        if '#' not in firsts[nonterm]:
                            firsts[nonterm].add('#')
                            changed = True

    print("\nComputed FIRST sets:")
    for k, v in firsts.items():
        print(f"FIRST({k}) = {{ {', '.join(sorted(v))} }}")
def computeAllFollows():
    global diction, follows
    for NT in diction:
        solset = set()
        sol = follow(NT)
        for g in sol:
            solset.add(g)
        follows[NT] = solset
    print("\nComputed FOLLOW sets:")
    for k, v in follows.items():
        print(f"FOLLOW({k}) = {{ {', '.join(v)} }}")

# ------------------ Parsing Table & Validation ------------------

def createParseTable():
    import copy
    global diction, firsts, follows, term_userdef

    ntlist = list(diction.keys())
    terminals = copy.deepcopy(term_userdef)
    if '$' not in terminals:
        terminals.append('$')  # ensure end-marker included

    # Initialize parsing table with empty strings
    mat = []
    for _ in diction:
        row = [''] * len(terminals)
        mat.append(row)

    grammar_is_LL = True

    # Helper: get index in matrix
    def get_nt_index(nt):
        return ntlist.index(nt)

    def get_term_index(t):
        return terminals.index(t)

    # Build parsing table
    for lhs in diction:
        rhs_list = diction[lhs]
        for rhs in rhs_list:
            res = first(rhs)
            # If epsilon in FIRST(rhs), add FOLLOW(lhs) as well
            if '#' in res:
                res_without_epsilon = [r for r in res if r != '#']
                res = res_without_epsilon + list(follows[lhs])
            for terminal in res:
                xnt = get_nt_index(lhs)
                yt = get_term_index(terminal)
                entry = f"{lhs}->{' '.join(rhs)}"
                if mat[xnt][yt] == '':
                    mat[xnt][yt] = entry
                else:
                    # Conflict: multiple productions for same cell => not LL(1)
                    if entry not in mat[xnt][yt]:
                        grammar_is_LL = False
                        mat[xnt][yt] += f", {entry}"

    # Print parsing table nicely
    print("\nParsing Table:")
    print(f"{'NT/T':<10}", end="")
    for term in terminals:
        print(f"{term:<15}", end="")
    print()
    for i, nt in enumerate(ntlist):
        print(f"{nt:<10}", end="")
        for j in range(len(terminals)):
            print(f"{mat[i][j]:<15}", end="")
        print()

    return mat, grammar_is_LL, terminals

def build_tree(tree_data):
    lines = []
    for level, symbol in tree_data:
        lines.append("  " * level + "|__ " + symbol)
    return "\n".join(lines)

def validateStringUsingStackBuffer(parsing_table, grammarll1, table_term_list, input_string, term_userdef, start_symbol):
    if not grammarll1:
        return "Grammar is not LL(1), parsing not possible."

    stack = [start_symbol, '$']
    input_buffer = ['$'] + input_string.split()[::-1]

    tree = []  # Parse tree as a list of (level, symbol)
    level_stack = [0]  # Parallel to stack, tracks indentation level

    output_lines = []
    output_lines.append(f"\n{'Buffer':>30} {'Stack':>30} {'Action':>40}")
    
    while True:
        if stack == ['$'] and input_buffer == ['$']:
            output_lines.append(f"{' '.join(input_buffer):>30} {' '.join(stack):>30} {'Valid String!':>40}")
            output_lines.append("\n🎄 Parse Tree:\n" + build_tree(tree))
            return "\n".join(output_lines)

        top_stack = stack[0]
        front_buffer = input_buffer[-1]
        cur_level = level_stack[0]

        if top_stack in term_userdef + ['$']:
            if top_stack == front_buffer:
                output_lines.append(f"{' '.join(input_buffer):>30} {' '.join(stack):>30} {'Match ' + top_stack:>40}")
                tree.append((cur_level, top_stack))
                stack.pop(0)
                level_stack.pop(0)
                input_buffer.pop()
            else:
                return "Invalid String! Terminal mismatch."
        else:
            try:
                row = list(diction.keys()).index(top_stack)
                col = table_term_list.index(front_buffer)
                entry = parsing_table[row][col]
                if entry == '':
                    return f"Invalid String! No rule for [{top_stack}][{front_buffer}]"
                
                output_lines.append(f"{' '.join(input_buffer):>30} {' '.join(stack):>30} {entry:>40}")

                lhs_rhs = entry.split("->")
                lhs = lhs_rhs[0].strip()
                rhs = lhs_rhs[1].strip().split() if lhs_rhs[1].strip() != '#' else []

                # Update parse tree
                tree.append((cur_level, lhs))
                rhs_levels = [cur_level + 1] * len(rhs)

                # Update stack
                stack = rhs + stack[1:]
                level_stack = rhs_levels + level_stack[1:]

            except ValueError:
                return f"Invalid String! Symbol not found in parse table."

# ------------------ Driver Code ------------------

def test_grammar(rules_list, nonterminals, terminals, input_str=None):
    global rules, nonterm_userdef, term_userdef, diction, firsts, follows, start_symbol

    rules = rules_list
    nonterm_userdef = nonterminals
    term_userdef = terminals
    diction = {}
    firsts = {}
    follows = {}

    computeAllFirsts()
    start_symbol = list(diction.keys())[0]
    computeAllFollows()

    parsing_table, is_ll1, term_list = createParseTable()

    print("\nGrammar is LL(1):", is_ll1)

    if input_str is not None:
        result = validateStringUsingStackBuffer(
            parsing_table,
            is_ll1,
            term_list,
            input_str,
            term_userdef,
            start_symbol
        )
        print(f"\nString '{input_str}' validation result:")
        print(result)

# -------------- GUI LOGIC ------------------

def parse_input():
    grammar = grammar_text.get("1.0", tk.END).strip().split("\n")
    nonterms = nonterminals_entry.get().strip().split(",")
    terms = terminals_entry.get().strip().split(",")
    input_string = input_string_entry.get().strip()

    if not grammar or not nonterms or not terms:
        messagebox.showwarning("Input Error", "Please provide all grammar components.")
        return

    try:
        output_text.delete("1.0", tk.END)
        test_grammar(grammar, nonterms, terms, input_string)
    except Exception as e:
        output_text.insert(tk.END, f"\n❌ Error: {e}\n")


def capture_print_output(func):
    import sys
    import io

    def wrapper(*args, **kwargs):
        buffer = io.StringIO()
        sys.stdout = buffer
        try:
            func(*args, **kwargs)
        finally:
            sys.stdout = sys.__stdout__
            output_text.insert(tk.END, buffer.getvalue())

    return wrapper


# Wrap test_grammar with print capture
test_grammar = capture_print_output(test_grammar)

# ------------------ GUI ------------------------

root = tk.Tk()
root.title("LL(1) Parser GUI")
root.geometry("800x700")
root.configure(bg="#f0f0f0")

tk.Label(root, text="Enter Grammar Rules (one per line):", bg="#f0f0f0").pack()
grammar_text = scrolledtext.ScrolledText(root, height=8, width=80)
grammar_text.pack()

tk.Label(root, text="Enter Non-Terminals (comma-separated):", bg="#f0f0f0").pack()
nonterminals_entry = tk.Entry(root, width=50)
nonterminals_entry.pack()

tk.Label(root, text="Enter Terminals (comma-separated):", bg="#f0f0f0").pack()
terminals_entry = tk.Entry(root, width=50)
terminals_entry.pack()

tk.Label(root, text="Enter Input String to Validate:", bg="#f0f0f0").pack()
input_string_entry = tk.Entry(root, width=50)
input_string_entry.pack()

tk.Button(root, text="Run LL(1) Parser", command=parse_input, bg="#007acc", fg="white", padx=10, pady=5).pack(pady=10)

tk.Label(root, text="Output:", bg="#f0f0f0").pack()
output_text = scrolledtext.ScrolledText(root, height=20, width=95)
output_text.pack()

root.mainloop()
