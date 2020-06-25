import functools
import sys

def tokenize(s):
    lst = []
    
    i = 0
    while i < len(s):
        if s[i] == '(' or s[i] == ')':
            lst.append(s[i])
            i += 1
        elif s[i] == ';':
            j = i
            while j < len(s) and s[j] != '\n':
                j += 1
            i = j
        elif s[i] == ' ' or s[i] == '\n':
            i += 1
        else:
            temp = ''
            j = i
            while j < len(s) and s[j] != ' ' and s[j] != ')' and s[j] != '(' and s[j] != '\n':
                temp += s[j]
                j += 1
            if temp != '':
                lst.append(temp)
            i = j
    return lst

def is_int(s):
    try:
        int(s)
        return True
    except:
        return False

def is_float(s):
    try:
        float(s)
        return True
    except:
        return False

def parse_helper(lst, i = 0):
    if i == len(lst):
        return None, None
    if is_int(lst[i]):
        return int(lst[i]), i + 1
    if is_float(lst[i]):
        return float(lst[i]), i + 1
    if lst[i] != '(' and lst[i] != ')':
        return lst[i], i + 1
    ret = []
    if lst[i] == '(':
        next_idx = i + 1
        while next_idx < len(lst) and lst[next_idx] != ')':
            ex, next_idx = parse_helper(lst, next_idx)
            ret.append(ex)
        if next_idx >= len(lst) or lst[next_idx] != ')':
            raise SyntaxError()
        return ret, next_idx + 1
    raise SyntaxError()

def parse(lst):
    ret, next_idx = parse_helper(lst)
    if len(lst) != next_idx:
        raise SyntaxError()
    return ret

def all_equal(lst):
    first = lst[0]
    for i in lst:
        if i != first:
            return False
    return True

def decreasing(lst):
    if (len(lst) <= 1):
        return True
    first = lst[0]
    for i in range(1, len(lst)):
        if lst[i] >= first:
            return False
        first = lst[i]
    return True

def nonincreasing(lst):
    if (len(lst) <= 1):
        return True
    first = lst[0]
    for i in range(1, len(lst)):
        if lst[i] > first:
            return False
        first = lst[i]
    return True

def increasing(lst):
    if (len(lst) <= 1):
        return True
    first = lst[0]
    for i in range(1, len(lst)):
        if lst[i] <= first:
            return False
        first = lst[i]
    return True

def nondecreasing(lst):
    if (len(lst) <= 1):
        return True
    first = lst[0]
    for i in range(1, len(lst)):
        if lst[i] < first:
            return False
        first = lst[i]
    return True

def not_func(lst):
    return not lst[0]

def list_func(args):
    if len(args) == 0:
        return LinkedList(None)
    elts = [LinkedList(i) for i in args]
    for i, j in zip(elts[:-1], elts[1:]):
        i.set_next_elt(j)
    return elts[0]

def empty_list_dec(func):
    def ret_func(arg):
        if arg.elt is None:
            raise EvaluationError()
        return func(arg)
    return ret_func

def car_func(arg):
    if arg.elt is None:
        raise EvaluationError()
    return arg.elt

def cdr_func(arg):
    if arg.elt is None:
        raise EvaluationError()
    return arg.next

def length_func(arg):
    if arg.elt == None:
        return 0
    count = 0
    for i in arg.list_iter():
        count+=1
    return count

def elt_at_index_func(arg, ind):
    if length_func(arg) <= ind:
        raise EvaluationError()
    count = 0
    for i in arg.list_iter():
        if count == ind:
            return i.elt
        count+=1

def concat_func(arg):
    cop = None
    if len(arg) == 0:
        return LinkedList(None)
    for i in reversed(arg):
        for j in range(length_func(i)-1, -1, -1):
            k = cop
            cop = LinkedList(elt_at_index_func(i, j))
            cop.set_next_elt(k)
    return cop

def map_func(func, lst):
    # if func not in carlae_builtins:
    #     func = result_and_env(func, func.env)[0]
    first = LinkedList(func([lst.elt]))
    ex = first
    while lst.next != None:
        lst = lst.next
        ex.next = LinkedList(func([lst.elt]))
        ex = ex.next
    return first

def filter_func(func, lst):
    if func([lst.elt]):
        first = LinkedList(lst.elt)
    else:
        first = None
    ex = first
    while lst.next != None:
        lst = lst.next
        if func([lst.elt]):
            ex.next = LinkedList(lst.elt)
            ex = ex.next
    return first

def reduce_func(func, lst, val):
    first = func([val, lst.elt])
    ex = func([val, lst.elt])
    while lst.next != None:
        lst = lst.next
        ex = func([ex, lst.elt])
    return ex

def evaluate_file(arg, eval_env=None):
    in_file = open(arg).read()
    return result_and_env(parse(tokenize(in_file)), eval_env)[0]


class EvaluationError(Exception):
    pass

class Environment(object):
    def __init__(self, parent = None, init_dict = {}):
        self.env_dict = {}
        self.parent = parent
        for i in init_dict:
            self.env_dict[i] = init_dict[i]
        #self.env_dict = {i: init_dict[i] for i in init_dict}
    
    def set(self, var_name, val):
        self.env_dict[var_name] = val
    
    def set_bang(self, var_name, val):
        cur_env = self
        while cur_env is not None and var_name not in cur_env.env_dict:
            cur_env = cur_env.parent
        if cur_env is None:
            raise EvaluationError()
        cur_env.set(var_name, val)

    def get(self, var_name):
        if isinstance(var_name, list):
            return None
        if var_name in self.env_dict:
            return self.env_dict[var_name]
        return self.parent.get(var_name) if self.parent is not None else None
    
    def copy(self):
        new = Environment(self.parent)
        for i in self.env_dict:
            new.env_dict[i] = self.env_dict[i]
        return new
    
    def __repr__(self):
        ret = 'Environment(\n'
        for i in self.env_dict:
            ret += str(i) + ' = ' + str(self.env_dict[i]) + '\n'
        ret += '\n)'
        return ret

class Function(object):
    def __init__(self, params, code, env):
        self.params = params
        self.code = code
        self.env = env
        for i in self.params:
            self.env.set(i, None)
    
    def set_values(self, args):
        if len(args) != len(self.params):
            raise EvaluationError()
        new_func = Function(self.params, self.code, self.env.copy())
        for j, i in enumerate(self.params):
            new_func.env.set(i, args[j])
        return new_func

    def __repr__(self):
        return 'function object'
    
    def __call__(self, args):
        new_func = self.set_values(args)
        return result_and_env(new_func.code, new_func.env)[0]
        
class LinkedList(object):
    def __init__(self, elt=None):
        self.elt = elt
        self.next = None
    
    def set_next_elt(self, next_elt):
        self.next = next_elt
    
    def list_iter(self):
        i = self
        while i is not None:
            yield i
            i = i.next

carlae_builtins = Environment(init_dict = {
                   '+': sum,
                   '-': lambda args: -args[0] if len(args) == 1 else args[0] - sum(args[1:]),
                   '*': lambda args: functools.reduce(lambda x, y: x * y, args),
                   '/': lambda args: args[0] / functools.reduce(lambda x, y: x * y, args[1:]),
                   '=?': all_equal,
                   '>': decreasing,
                   '>=': nonincreasing,
                   '<': increasing,
                   '<=': nondecreasing,
                   'not': not_func,
                   '#t': True,
                   '#f': False,
                   'list': list_func,
                   'car': lambda arg: car_func(arg[0]), #empty_list_dec(lambda arg: arg.elt),
                   'cdr': lambda arg: cdr_func(arg[0]), #empty_list_dec(lambda arg: arg.next),
                   'length': lambda arg: length_func(arg[0]),
                   'elt-at-index': lambda arg: elt_at_index_func(arg[0], arg[1]),
                   'concat': concat_func,
                   'map': lambda arg: map_func(arg[0], arg[1]),
                   'filter': lambda arg: filter_func(arg[0], arg[1]),
                   'reduce': lambda arg: reduce_func(arg[0], arg[1], arg[2]),
                   'begin': lambda arg: arg[-1]
                   })

def result_and_env(inp, env = None):
    if env is None:
        env = Environment(carlae_builtins)
    if isinstance(inp, list) and len(inp) == 0:
        raise EvaluationError()
    if is_int(inp) or is_float(inp):
        return inp, env
    if isinstance(inp, str):
        sym = env.get(inp)
        if sym is not None:
            return sym, env
        raise EvaluationError()
    # if isinstance(inp, list):
    #     if len(inp) == 0:
    #         raise EvaluationError()
        # what if it is define
    if inp[0] == 'define':
        # if (len(inp) != 3):
        #     raise EvaluationError()
        if ((not isinstance(inp[1], str)) and (not isinstance(inp[1], list))):
            raise EvaluationError()
        new_env = Environment(env)
        if isinstance(inp[1], list):
            env.set(inp[1][0], Function(inp[1][1:], inp[2], new_env))
            return env.get(inp[1][0]), env
        else:
            env.set(inp[1], result_and_env(inp[2], env)[0])
            return env.get(inp[1]), env

    if inp[0] == 'lambda':
        if len(inp) != 3:
            raise EvaluationError()
        new_env = Environment(env)
        func = Function(inp[1], inp[2], new_env)
        return func, env
    
    if inp[0] == 'if':
        new_env = Environment(env)
        if result_and_env(inp[1], env)[0] is True or result_and_env(inp[1], env)[0] == '#t':
            return result_and_env(inp[2], env)
        else:
            return result_and_env(inp[3], env)
    
    if inp[0] == 'and':
        new_env = Environment(env)
        for i in inp[1:]:
            if result_and_env(i, env)[0] is False:
                return False, env
        return True, env
    
    if inp[0] == 'or':
        new_env = Environment(env)
        for i in inp[1:]:
            if result_and_env(i, env)[0] is True:
                return True, env
        return False, env
    
    if inp[0] == 'let':
        inp_vars = inp[1]
        new_env = Environment(env)
        for i in inp_vars:
            new_env.set(i[0], result_and_env(i[1], env)[0])
        return result_and_env(inp[2], new_env)[0], env
    
    if inp[0] == 'set!':
        #new_env = env.get(inp[1])
        # if not env[inp[1]]:
        #     raise EvaluationError()
        val = result_and_env(inp[2], env)[0]
        env.set_bang(inp[1], val)
        return val, env

    
    # what if it isn't define
    if (not isinstance(inp[0], list)) and (not isinstance(inp[0], str)):
        raise EvaluationError()

    ex = []
    for i in inp[1:]:
        new_env = Environment(env)
        ex.append(result_and_env(i, env)[0])
    new_env = Environment(env)
    func = result_and_env(inp[0], env)[0]
    return func(ex), env

def evaluate(inp, env = None):
    return result_and_env(inp, env)[0]

def repl():
    inp = None
    env = Environment(carlae_builtins)
    if len(sys.argv[1:]) > 0:
        for i in sys.argv[1:]:
            evaluate_file(i, env)

    while inp != 'QUIT':
        inp = input('in> ')
        if inp == 'QUIT':
            break
        try:
            ret, new_env = result_and_env(parse(tokenize(inp)), env)
            env = new_env
            print('out>', ret)
        except Exception as e:
            print('out>', str(e))

if __name__ == '__main__':
    repl()
