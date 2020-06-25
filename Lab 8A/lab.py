import functools

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
        
carlae_builtins = Environment({
                   '+': sum,
                   '-': lambda args: -args[0] if len(args) == 1 else args[0] - sum(args[1:]),
                   '*': lambda args: functools.reduce(lambda x, y: x * y, args),
                   '/': lambda args: args[0] / functools.reduce(lambda x, y: x * y, args[1:])})

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
    # what if it isn't define
    # args = [result_and_env(i, env)[0] for i in inp]
    # if not callable(args[0]):
    #     raise EvaluationError()
    # return args[0](args[1:]), env
    if (not isinstance(inp[0], list)) and (not isinstance(inp[0], str)):
        raise EvaluationError()

    ex = []
    for i in inp[1:]:
        new_env = Environment(env)
        ex.append(result_and_env(i, env)[0])
    new_env = Environment(env)
    func = result_and_env(inp[0], env)[0]
    if isinstance(func, Function):
        func = func.set_values(ex)
        return result_and_env(func.code, func.env)[0], env
    return func(ex), env

def evaluate(inp, env = None):
    return result_and_env(inp, env)[0]

def repl():
    inp = None
    env = Environment(carlae_builtins)
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
