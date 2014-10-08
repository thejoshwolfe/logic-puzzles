#!/usr/bin/env python3

import itertools

class Contradiction(Exception):
  pass
def solve(properties, constraints):
  value_to_possible_values = {v: values
                              for values in properties
                                for v in values}
  all_value_set_pairs = frozenset(frozenset(x) for x in itertools.combinations(properties, 2))
  all_value_pairs = frozenset(frozenset(value_pair)
                              for value_set_pair in all_value_set_pairs
                                for value_pair in itertools.product(*value_set_pair))
  knowledge = {}
  def report_progress(blurb):
    done = len(knowledge)
    total = len(all_value_pairs)
    percent = 100*done/total
    print("{}/{} {:05.2f}%: {}".format(done, total, percent, blurb))
  report_progress("init")

  def claim(key, value):
    old_value = knowledge.get(key, None)
    if old_value != None and old_value != value:
      raise Contradiction()
    knowledge[key] = value

  def print_winners():
    value_to_family = {value: frozenset(value) for value_set in properties for value in value_set}
    for (value_a, value_b), known in knowledge.items():
      if not known: continue
      family = frozenset(itertools.chain(value_to_family[value_a], value_to_family[value_b]))
      value_to_family[value_a] = value_to_family[value_b] = family
    families = frozenset(value_to_family.values())
    print_frozenset(families)

  while True:
    print("============")

    previous_knowledge_magnitude = len(knowledge)
    if previous_knowledge_magnitude == len(all_value_pairs):
      print_winners()
      break

    for constraint in constraints:
      the_scenario = None
      for scenario in constraint:
        for pair in scenario:
          if knowledge.get(pair, None) == False:
            break # this scenario doesn't work
        else:
          # this scenario works
          if the_scenario == None:
            the_scenario = scenario
          else:
            # multiple scenarios work. not helpful.
            break
      else:
        if the_scenario != None:
          for pair in the_scenario:
            claim(pair, True)
    report_progress("constraints")

    for value_pair, is_correct in list(knowledge.items()):
      if not is_correct: continue
      for value_a, value_b in forwards_and_backwards(value_pair):
        for other_value in value_to_possible_values[value_a]:
          if value_a == other_value: continue
          claim(frozenset([other_value, value_b]),  False)
    report_progress("plus sign exclusion")

    for value_set_pair in all_value_set_pairs:
      for value_set_a, value_set_b in forwards_and_backwards(value_set_pair):
        for pegged_value in value_set_a:
          the_unknown_slot = None
          for value in value_set_b:
            key = frozenset([pegged_value, value])
            known = knowledge.get(key, None)
            if known == True: break # exclusion took care of this
            if known != None: continue
            # only allowed 1 unknown
            if the_unknown_slot == None:
              the_unknown_slot = key
            else:
              break
          else:
            if the_unknown_slot != None:
              claim(the_unknown_slot, True)
    report_progress("process of elimination")

    for value_pair, is_correct in list(knowledge.items()):
      if not is_correct: continue
      from_value_sets = tuple(value_to_possible_values[value] for value in value_pair)
      for value_set in properties:
        if value_set in from_value_sets: continue
        for value_a, value_b in forwards_and_backwards(value_pair):
          for value_c in value_set:
            try: known = knowledge[frozenset([value_b, value_c])]
            except KeyError: continue
            claim(frozenset([value_a, value_c]), known)
    report_progress("transitivity")

    if len(knowledge) == previous_knowledge_magnitude:
      # start guessing
      print("ambiguous")
      for random_pair in all_value_pairs:
        if random_pair in knowledge: continue
        new_constraints = frozenset(itertools.chain(constraints, [DirectConstraint(*random_pair)]))
        try:
          print(">>>>>>>>>>>> guess: " + repr(random_pair))
          solve(properties, new_constraints)
        except Contradiction:
          print("<<<<<<<<<<<< nope.avi")
          continue
        else:
          print("<<<<<<<<<<<< got it")
          break
      break

def forwards_and_backwards(s):
  t = tuple(s)
  return (t, reversed(t))


def print_frozenset(s):
  def deep_to_tuple(s):
    if type(s) == frozenset:
      s = tuple(sorted(deep_to_tuple(x) for x in s))
    elif type(s) == dict:
      s = {deep_to_tuple(k): deep_to_tuple(v) for k, v in s.items()}
    return s
  print(deep_to_tuple(s))

def VariableConstraint(value_a, value_b, pairing_options):
  return frozenset([frozenset([frozenset([value_a, other_a]), frozenset([value_b, other_b])])
                   for other_a, other_b in pairing_options])
def DirectConstraint(value_a, value_b):
  return frozenset([frozenset([frozenset([value_a, value_b])])])

properties = frozenset([
  frozenset(["1", "2", "3"]),
  frozenset(["a", "b", "c"]),
])

constraints = frozenset([
  VariableConstraint("a", "b", [
    # "a" and "b" are neighbors
    ("1", "2"),
    ("2", "1"),
    ("2", "3"),
    ("3", "2"),
  ]),
  VariableConstraint("b", "c", [
    # "b" immediately preceeds "c"
    ("1", "2"),
    ("2", "3"),
  ]),
  # DirectConstraint("a", "1"),
  # DirectConstraint("b", "y"),
  # DirectConstraint("3", "z"),
])
solve(properties, constraints)
