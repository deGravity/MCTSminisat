# This file was automatically generated by SWIG (http://www.swig.org).
# Version 3.0.12
#
# Do not make changes to this file unless you know what you are doing--modify
# the SWIG interface file instead.

from sys import version_info as _swig_python_version_info
if _swig_python_version_info >= (2, 7, 0):
    def swig_import_helper():
        import importlib
        pkg = __name__.rpartition('.')[0]
        mname = '.'.join((pkg, '_GymSolver')).lstrip('.')
        try:
            return importlib.import_module(mname)
        except ImportError:
            return importlib.import_module('_GymSolver')
    _GymSolver = swig_import_helper()
    del swig_import_helper
elif _swig_python_version_info >= (2, 6, 0):
    def swig_import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_GymSolver', [dirname(__file__)])
        except ImportError:
            import _GymSolver
            return _GymSolver
        try:
            _mod = imp.load_module('_GymSolver', fp, pathname, description)
        finally:
            if fp is not None:
                fp.close()
        return _mod
    _GymSolver = swig_import_helper()
    del swig_import_helper
else:
    import _GymSolver
del _swig_python_version_info

try:
    _swig_property = property
except NameError:
    pass  # Python < 2.2 doesn't have 'property'.

try:
    import builtins as __builtin__
except ImportError:
    import __builtin__

def _swig_setattr_nondynamic(self, class_type, name, value, static=1):
    if (name == "thisown"):
        return self.this.own(value)
    if (name == "this"):
        if type(value).__name__ == 'SwigPyObject':
            self.__dict__[name] = value
            return
    method = class_type.__swig_setmethods__.get(name, None)
    if method:
        return method(self, value)
    if (not static):
        if _newclass:
            object.__setattr__(self, name, value)
        else:
            self.__dict__[name] = value
    else:
        raise AttributeError("You cannot add attributes to %s" % self)


def _swig_setattr(self, class_type, name, value):
    return _swig_setattr_nondynamic(self, class_type, name, value, 0)


def _swig_getattr(self, class_type, name):
    if (name == "thisown"):
        return self.this.own()
    method = class_type.__swig_getmethods__.get(name, None)
    if method:
        return method(self)
    raise AttributeError("'%s' object has no attribute '%s'" % (class_type.__name__, name))


def _swig_repr(self):
    try:
        strthis = "proxy of " + self.this.__repr__()
    except __builtin__.Exception:
        strthis = ""
    return "<%s.%s; %s >" % (self.__class__.__module__, self.__class__.__name__, strthis,)

try:
    _object = object
    _newclass = 1
except __builtin__.Exception:
    class _object:
        pass
    _newclass = 0

class GymSolver(_object):
    __swig_setmethods__ = {}
    __setattr__ = lambda self, name, value: _swig_setattr(self, GymSolver, name, value)
    __swig_getmethods__ = {}
    __getattr__ = lambda self, name: _swig_getattr(self, GymSolver, name)
    __repr__ = _swig_repr

    def __init__(self, arg2):
        this = _GymSolver.new_GymSolver(arg2)
        try:
            self.this.append(this)
        except __builtin__.Exception:
            self.this = this

    def step(self, arg2):
        return _GymSolver.GymSolver_step(self, arg2)

    def getReward(self):
        return _GymSolver.GymSolver_getReward(self)

    def getDone(self):
        return _GymSolver.GymSolver_getDone(self)

    def getState(self):
        return _GymSolver.GymSolver_getState(self)
    __swig_destroy__ = _GymSolver.delete_GymSolver
    __del__ = lambda self: None
GymSolver_swigregister = _GymSolver.GymSolver_swigregister
GymSolver_swigregister(GymSolver)

# This file is compatible with both classic and new-style classes.

# Following file is the real GymSAT part
import numpy as np
import gym
from gym import spaces
import random
class gym_sat_Env(gym.Env):
	
	"""
		this class is a gym environment for Reinforcement Learning algorithms
		max_clause: the number of rows in state representation
		max_var: the number of columns in state representation
	"""
	def __init__(self, max_clause=100, max_var=20): 
		self.max_clause = max_clause
		self.max_var = max_var
		self.observation_space = np.zeros((max_clause, max_var, 1))
		self.action_space = spaces.Discrete(2*self.max_var)
		self.score = 0
		self.exp_av_score = 15 # some randomly initialized initial average value
		
	"""
		this function parse the state into sparse matrix with -1 or 1 values
		Can handle the case when state is empty and the SAT is either broken or solved already
	"""
	def parse_state(self):
		curr_state = np.zeros((self.max_clause, self.max_var, 1), dtype = np.int8)
		clause_counter = 0 # this tracks the current row-to-write (which is permutable!)
		actionSet = set() # this set tracks all allowed actions for this state
		# if S is already Done, should return here.
		if self.S.getDone():
			return curr_state, clause_counter, True, actionSet
		# S is not yet Done, parse and return real state
		for line in self.S.getState().split('\n'):
			if line.startswith("p cnf"): # this is the header of a cnf problem # p cnf 20 90
				header = line.split(" ")
				num_var = int(header[2])
				num_clause = int(header[3])
				assert (num_var <= self.max_var)
				# assert (num_clause <= self.max_clause) # remove this assert (might be wrong if we learnt too many clauses and restarted)
			elif line.startswith("c"):
				continue
			else: # clause data line # -11 -17 20 0
				literals = line.split(" ")
				n = len(literals)
				for j in range(n-1):
					number = int(literals[j])
					value = 1 if number > 0 else -1
					curr_state[clause_counter, abs(number) - 1] = value
					actionSet.add(number)
				clause_counter += 1
				if clause_counter >= self.max_clause: # add a safe guard for overflow of number of clauses
					break;
		return curr_state, clause_counter, False, actionSet

	# TODO: add a randomlization pick of files from a file list, give that choice to "satProb"
	def random_pick_satProb(self):
		# uf20-91/uf20-0 i .cnf, where i is 1 to 1000 
		return "uf20-91/uf20-0" + str(random.randint(1,1000)) + ".cnf"

	"""
		this function reports to the agent about the environment
	"""
	def report_to_agent(self):
		return self.curr_state, self.S.getReward(), self.isSolved, {}

	"""
		this function reset the environment and return the initial state
	"""
	def reset(self):
		self.exp_av_score = self.exp_av_score * 0.98 + self.score * 0.02
		self.score = 0
		print(round(self.exp_av_score), end=".", flush = True)
		#print("r", end="", flush=True)
		self.S = GymSolver(self.random_pick_satProb())
		self.curr_state, self.clause_counter, self.isSolved, self.actionSet = self.parse_state()
		return self.curr_state

	"""
		this function make a step based on parameter input
	"""
	def step(self, decision):
		self.score += 1
		if (decision < 0): # this is to say that let minisat pick the decision
			decision = 32767
		elif (decision % 2 == 0): # this is to say that pick decision and assign positive value
			decision = int(decision / 2 + 1)
		else: # this is to say that pick decision and assign negative value
			decision = 0 - int(decision / 2 + 1) 
		if (decision in self.actionSet) or (decision == 32767):
			self.S.step(decision)
			self.curr_state, self.clause_counter, self.isSolved, self.actionSet = self.parse_state()
			return self.report_to_agent()
		else:
			return self.report_to_agent() 

	"""
		this function renders the sat problem
	"""
	def render(self, mode='human', close=False):
		pass

# this is the Dynamic action space used for gym environment
class Dynamic(gym.Space):

	"""
	The Dynamic takes a set of int as allowed actions
	"""
	def __init__(self, actionSet):
		self.available_actions = actionSet

	def disable_actions(self, actions):
		""" You would call this method inside your environment to remove available actions"""
		self.available_actions = [action for action in self.available_actions if action not in actions]
		return self.available_actions

	def enable_actions(self, actions):
		""" You would call this method inside your environment to enable actions"""
		self.available_actions = self.available_actions.append(actions)
		return self.available_actions

	def sample(self):
		return random.sample(self.available_actions, 1)[0]

	def contains(self, x):
		return x in self.available_actions

	@property
	def shape(self):
		return ()

	def __repr__(self):
		return "Dynamic(%d)" % self.n

	def __eq__(self, other):
		return self.available_actions == other.available_actions
