"""Python abstract syntax node definitions

This file is automatically generated.
"""
from types import TupleType, ListType
from consts import CO_VARARGS, CO_VARKEYWORDS

def flatten(list):
    l = []
    for elt in list:
        t = type(elt)
        if t is TupleType or t is ListType:
            for elt2 in flatten(elt):
                l.append(elt2)
        else:
            l.append(elt)
    return l

def flatten_nodes(list):
    return [n for n in flatten(list) if isinstance(n, Node)]

def asList(nodearg):
    l = []
    for item in nodearg:
        if hasattr(item, "asList"):
            l.append(item.asList())
        else:
            t = type(item)
            if t is TupleType or t is ListType:
                l.append(tuple(asList(item)))
            else:
                l.append(item)
    return l

nodes = {}

class Node: # an abstract base class
    lineno = None # provide a lineno for nodes that don't have one
    def getType(self):
        pass # implemented by subclass
    def getChildren(self):
        pass # implemented by subclasses
    def asList(self):
        return tuple(asList(self.getChildren()))
    def getChildNodes(self):
        pass # implemented by subclasses

class EmptyNode(Node):
    pass

class Slice(Node):
    nodes["slice"] = "Slice"
    def __init__(self, expr, flags, lower, upper):
        self.expr = expr
        self.flags = flags
        self.lower = lower
        self.upper = upper

    def getChildren(self):
        children = []
        children.append(self.expr)
        children.append(self.flags)
        children.append(self.lower)
        children.append(self.upper)
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.append(self.expr)
        if self.lower is not None:            nodelist.append(self.lower)
        if self.upper is not None:            nodelist.append(self.upper)
        return tuple(nodelist)

    def __repr__(self):
        return "Slice(%s, %s, %s, %s)" % (repr(self.expr), repr(self.flags), repr(self.lower), repr(self.upper))

class Const(Node):
    nodes["const"] = "Const"
    def __init__(self, value):
        self.value = value

    def getChildren(self):
        return self.value,

    def getChildNodes(self):
        return ()

    def __repr__(self):
        return "Const(%s)" % (repr(self.value),)

class Raise(Node):
    nodes["raise"] = "Raise"
    def __init__(self, expr1, expr2, expr3):
        self.expr1 = expr1
        self.expr2 = expr2
        self.expr3 = expr3

    def getChildren(self):
        children = []
        children.append(self.expr1)
        children.append(self.expr2)
        children.append(self.expr3)
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        if self.expr1 is not None:            nodelist.append(self.expr1)
        if self.expr2 is not None:            nodelist.append(self.expr2)
        if self.expr3 is not None:            nodelist.append(self.expr3)
        return tuple(nodelist)

    def __repr__(self):
        return "Raise(%s, %s, %s)" % (repr(self.expr1), repr(self.expr2), repr(self.expr3))

class For(Node):
    nodes["for"] = "For"
    def __init__(self, assign, list, body, else_):
        self.assign = assign
        self.list = list
        self.body = body
        self.else_ = else_

    def getChildren(self):
        children = []
        children.append(self.assign)
        children.append(self.list)
        children.append(self.body)
        children.append(self.else_)
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.append(self.assign)
        nodelist.append(self.list)
        nodelist.append(self.body)
        if self.else_ is not None:            nodelist.append(self.else_)
        return tuple(nodelist)

    def __repr__(self):
        return "For(%s, %s, %s, %s)" % (repr(self.assign), repr(self.list), repr(self.body), repr(self.else_))

class AssTuple(Node):
    nodes["asstuple"] = "AssTuple"
    def __init__(self, nodes):
        self.nodes = nodes

    def getChildren(self):
        children = []
        children.extend(flatten(self.nodes))
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.extend(flatten_nodes(self.nodes))
        return tuple(nodelist)

    def __repr__(self):
        return "AssTuple(%s)" % (repr(self.nodes),)

class Mul(Node):
    nodes["mul"] = "Mul"
    def __init__(self, (left, right)):
        self.left = left
        self.right = right

    def getChildren(self):
        return self.left, self.right

    def getChildNodes(self):
        return self.left, self.right

    def __repr__(self):
        return "Mul((%s, %s))" % (repr(self.left), repr(self.right))

class Invert(Node):
    nodes["invert"] = "Invert"
    def __init__(self, expr):
        self.expr = expr

    def getChildren(self):
        return self.expr,

    def getChildNodes(self):
        return self.expr,

    def __repr__(self):
        return "Invert(%s)" % (repr(self.expr),)

class RightShift(Node):
    nodes["rightshift"] = "RightShift"
    def __init__(self, (left, right)):
        self.left = left
        self.right = right

    def getChildren(self):
        return self.left, self.right

    def getChildNodes(self):
        return self.left, self.right

    def __repr__(self):
        return "RightShift((%s, %s))" % (repr(self.left), repr(self.right))

class AssList(Node):
    nodes["asslist"] = "AssList"
    def __init__(self, nodes):
        self.nodes = nodes

    def getChildren(self):
        children = []
        children.extend(flatten(self.nodes))
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.extend(flatten_nodes(self.nodes))
        return tuple(nodelist)

    def __repr__(self):
        return "AssList(%s)" % (repr(self.nodes),)

class From(Node):
    nodes["from"] = "From"
    def __init__(self, modname, names):
        self.modname = modname
        self.names = names

    def getChildren(self):
        return self.modname, self.names

    def getChildNodes(self):
        return ()

    def __repr__(self):
        return "From(%s, %s)" % (repr(self.modname), repr(self.names))

class Getattr(Node):
    nodes["getattr"] = "Getattr"
    def __init__(self, expr, attrname):
        self.expr = expr
        self.attrname = attrname

    def getChildren(self):
        return self.expr, self.attrname

    def getChildNodes(self):
        return self.expr,

    def __repr__(self):
        return "Getattr(%s, %s)" % (repr(self.expr), repr(self.attrname))

class Dict(Node):
    nodes["dict"] = "Dict"
    def __init__(self, items):
        self.items = items

    def getChildren(self):
        children = []
        children.extend(flatten(self.items))
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.extend(flatten_nodes(self.items))
        return tuple(nodelist)

    def __repr__(self):
        return "Dict(%s)" % (repr(self.items),)

class Module(Node):
    nodes["module"] = "Module"
    def __init__(self, doc, node):
        self.doc = doc
        self.node = node

    def getChildren(self):
        return self.doc, self.node

    def getChildNodes(self):
        return self.node,

    def __repr__(self):
        return "Module(%s, %s)" % (repr(self.doc), repr(self.node))

class Expression(Node):
    # Expression is an artificial node class to support "eval"
    nodes["expression"] = "Expression"
    def __init__(self, node):
        self.node = node

    def getChildren(self):
        return self.node,

    def getChildNodes(self):
        return self.node,

    def __repr__(self):
        return "Expression(%s)" % (repr(self.node))

class UnaryAdd(Node):
    nodes["unaryadd"] = "UnaryAdd"
    def __init__(self, expr):
        self.expr = expr

    def getChildren(self):
        return self.expr,

    def getChildNodes(self):
        return self.expr,

    def __repr__(self):
        return "UnaryAdd(%s)" % (repr(self.expr),)

class Ellipsis(Node):
    nodes["ellipsis"] = "Ellipsis"
    def __init__(self, ):
        pass

    def getChildren(self):
        return ()

    def getChildNodes(self):
        return ()

    def __repr__(self):
        return "Ellipsis()"

class Print(Node):
    nodes["print"] = "Print"
    def __init__(self, nodes, dest):
        self.nodes = nodes
        self.dest = dest

    def getChildren(self):
        children = []
        children.extend(flatten(self.nodes))
        children.append(self.dest)
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.extend(flatten_nodes(self.nodes))
        if self.dest is not None:            nodelist.append(self.dest)
        return tuple(nodelist)

    def __repr__(self):
        return "Print(%s, %s)" % (repr(self.nodes), repr(self.dest))

class Import(Node):
    nodes["import"] = "Import"
    def __init__(self, names):
        self.names = names

    def getChildren(self):
        return self.names,

    def getChildNodes(self):
        return ()

    def __repr__(self):
        return "Import(%s)" % (repr(self.names),)

class Subscript(Node):
    nodes["subscript"] = "Subscript"
    def __init__(self, expr, flags, subs):
        self.expr = expr
        self.flags = flags
        self.subs = subs

    def getChildren(self):
        children = []
        children.append(self.expr)
        children.append(self.flags)
        children.extend(flatten(self.subs))
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.append(self.expr)
        nodelist.extend(flatten_nodes(self.subs))
        return tuple(nodelist)

    def __repr__(self):
        return "Subscript(%s, %s, %s)" % (repr(self.expr), repr(self.flags), repr(self.subs))

class TryExcept(Node):
    nodes["tryexcept"] = "TryExcept"
    def __init__(self, body, handlers, else_):
        self.body = body
        self.handlers = handlers
        self.else_ = else_

    def getChildren(self):
        children = []
        children.append(self.body)
        children.extend(flatten(self.handlers))
        children.append(self.else_)
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.append(self.body)
        nodelist.extend(flatten_nodes(self.handlers))
        if self.else_ is not None:            nodelist.append(self.else_)
        return tuple(nodelist)

    def __repr__(self):
        return "TryExcept(%s, %s, %s)" % (repr(self.body), repr(self.handlers), repr(self.else_))

class Or(Node):
    nodes["or"] = "Or"
    def __init__(self, nodes):
        self.nodes = nodes

    def getChildren(self):
        children = []
        children.extend(flatten(self.nodes))
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.extend(flatten_nodes(self.nodes))
        return tuple(nodelist)

    def __repr__(self):
        return "Or(%s)" % (repr(self.nodes),)

class Name(Node):
    nodes["name"] = "Name"
    def __init__(self, name):
        self.name = name

    def getChildren(self):
        return self.name,

    def getChildNodes(self):
        return ()

    def __repr__(self):
        return "Name(%s)" % (repr(self.name),)

class Function(Node):
    nodes["function"] = "Function"
    def __init__(self, name, argnames, defaults, flags, doc, code):
        self.name = name
        self.argnames = argnames
        self.defaults = defaults
        self.flags = flags
        self.doc = doc
        self.code = code
        self.varargs = self.kwargs = None
        if flags & CO_VARARGS:
            self.varargs = 1
        if flags & CO_VARKEYWORDS:
            self.kwargs = 1



    def getChildren(self):
        children = []
        children.append(self.name)
        children.append(self.argnames)
        children.extend(flatten(self.defaults))
        children.append(self.flags)
        children.append(self.doc)
        children.append(self.code)
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.extend(flatten_nodes(self.defaults))
        nodelist.append(self.code)
        return tuple(nodelist)

    def __repr__(self):
        return "Function(%s, %s, %s, %s, %s, %s)" % (repr(self.name), repr(self.argnames), repr(self.defaults), repr(self.flags), repr(self.doc), repr(self.code))

class Assert(Node):
    nodes["assert"] = "Assert"
    def __init__(self, test, fail):
        self.test = test
        self.fail = fail

    def getChildren(self):
        children = []
        children.append(self.test)
        children.append(self.fail)
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.append(self.test)
        if self.fail is not None:            nodelist.append(self.fail)
        return tuple(nodelist)

    def __repr__(self):
        return "Assert(%s, %s)" % (repr(self.test), repr(self.fail))

class Return(Node):
    nodes["return"] = "Return"
    def __init__(self, value):
        self.value = value

    def getChildren(self):
        return self.value,

    def getChildNodes(self):
        return self.value,

    def __repr__(self):
        return "Return(%s)" % (repr(self.value),)

class Power(Node):
    nodes["power"] = "Power"
    def __init__(self, (left, right)):
        self.left = left
        self.right = right

    def getChildren(self):
        return self.left, self.right

    def getChildNodes(self):
        return self.left, self.right

    def __repr__(self):
        return "Power((%s, %s))" % (repr(self.left), repr(self.right))

class Exec(Node):
    nodes["exec"] = "Exec"
    def __init__(self, expr, locals, globals):
        self.expr = expr
        self.locals = locals
        self.globals = globals

    def getChildren(self):
        children = []
        children.append(self.expr)
        children.append(self.locals)
        children.append(self.globals)
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.append(self.expr)
        if self.locals is not None:            nodelist.append(self.locals)
        if self.globals is not None:            nodelist.append(self.globals)
        return tuple(nodelist)

    def __repr__(self):
        return "Exec(%s, %s, %s)" % (repr(self.expr), repr(self.locals), repr(self.globals))

class Stmt(Node):
    nodes["stmt"] = "Stmt"
    def __init__(self, nodes):
        self.nodes = nodes

    def getChildren(self):
        children = []
        children.extend(flatten(self.nodes))
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.extend(flatten_nodes(self.nodes))
        return tuple(nodelist)

    def __repr__(self):
        return "Stmt(%s)" % (repr(self.nodes),)

class Sliceobj(Node):
    nodes["sliceobj"] = "Sliceobj"
    def __init__(self, nodes):
        self.nodes = nodes

    def getChildren(self):
        children = []
        children.extend(flatten(self.nodes))
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.extend(flatten_nodes(self.nodes))
        return tuple(nodelist)

    def __repr__(self):
        return "Sliceobj(%s)" % (repr(self.nodes),)

class Break(Node):
    nodes["break"] = "Break"
    def __init__(self, ):
        pass

    def getChildren(self):
        return ()

    def getChildNodes(self):
        return ()

    def __repr__(self):
        return "Break()"

class Bitand(Node):
    nodes["bitand"] = "Bitand"
    def __init__(self, nodes):
        self.nodes = nodes

    def getChildren(self):
        children = []
        children.extend(flatten(self.nodes))
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.extend(flatten_nodes(self.nodes))
        return tuple(nodelist)

    def __repr__(self):
        return "Bitand(%s)" % (repr(self.nodes),)

class FloorDiv(Node):
    nodes["floordiv"] = "FloorDiv"
    def __init__(self, (left, right)):
        self.left = left
        self.right = right

    def getChildren(self):
        return self.left, self.right

    def getChildNodes(self):
        return self.left, self.right

    def __repr__(self):
        return "FloorDiv((%s, %s))" % (repr(self.left), repr(self.right))

class TryFinally(Node):
    nodes["tryfinally"] = "TryFinally"
    def __init__(self, body, final):
        self.body = body
        self.final = final

    def getChildren(self):
        return self.body, self.final

    def getChildNodes(self):
        return self.body, self.final

    def __repr__(self):
        return "TryFinally(%s, %s)" % (repr(self.body), repr(self.final))

class Not(Node):
    nodes["not"] = "Not"
    def __init__(self, expr):
        self.expr = expr

    def getChildren(self):
        return self.expr,

    def getChildNodes(self):
        return self.expr,

    def __repr__(self):
        return "Not(%s)" % (repr(self.expr),)

class Class(Node):
    nodes["class"] = "Class"
    def __init__(self, name, bases, doc, code):
        self.name = name
        self.bases = bases
        self.doc = doc
        self.code = code

    def getChildren(self):
        children = []
        children.append(self.name)
        children.extend(flatten(self.bases))
        children.append(self.doc)
        children.append(self.code)
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.extend(flatten_nodes(self.bases))
        nodelist.append(self.code)
        return tuple(nodelist)

    def __repr__(self):
        return "Class(%s, %s, %s, %s)" % (repr(self.name), repr(self.bases), repr(self.doc), repr(self.code))

class Mod(Node):
    nodes["mod"] = "Mod"
    def __init__(self, (left, right)):
        self.left = left
        self.right = right

    def getChildren(self):
        return self.left, self.right

    def getChildNodes(self):
        return self.left, self.right

    def __repr__(self):
        return "Mod((%s, %s))" % (repr(self.left), repr(self.right))

class Printnl(Node):
    nodes["printnl"] = "Printnl"
    def __init__(self, nodes, dest):
        self.nodes = nodes
        self.dest = dest

    def getChildren(self):
        children = []
        children.extend(flatten(self.nodes))
        children.append(self.dest)
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.extend(flatten_nodes(self.nodes))
        if self.dest is not None:            nodelist.append(self.dest)
        return tuple(nodelist)

    def __repr__(self):
        return "Printnl(%s, %s)" % (repr(self.nodes), repr(self.dest))

class Tuple(Node):
    nodes["tuple"] = "Tuple"
    def __init__(self, nodes):
        self.nodes = nodes

    def getChildren(self):
        children = []
        children.extend(flatten(self.nodes))
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.extend(flatten_nodes(self.nodes))
        return tuple(nodelist)

    def __repr__(self):
        return "Tuple(%s)" % (repr(self.nodes),)

class AssAttr(Node):
    nodes["assattr"] = "AssAttr"
    def __init__(self, expr, attrname, flags):
        self.expr = expr
        self.attrname = attrname
        self.flags = flags

    def getChildren(self):
        return self.expr, self.attrname, self.flags

    def getChildNodes(self):
        return self.expr,

    def __repr__(self):
        return "AssAttr(%s, %s, %s)" % (repr(self.expr), repr(self.attrname), repr(self.flags))

class Keyword(Node):
    nodes["keyword"] = "Keyword"
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr

    def getChildren(self):
        return self.name, self.expr

    def getChildNodes(self):
        return self.expr,

    def __repr__(self):
        return "Keyword(%s, %s)" % (repr(self.name), repr(self.expr))

class AugAssign(Node):
    nodes["augassign"] = "AugAssign"
    def __init__(self, node, op, expr):
        self.node = node
        self.op = op
        self.expr = expr

    def getChildren(self):
        return self.node, self.op, self.expr

    def getChildNodes(self):
        return self.node, self.expr

    def __repr__(self):
        return "AugAssign(%s, %s, %s)" % (repr(self.node), repr(self.op), repr(self.expr))

class List(Node):
    nodes["list"] = "List"
    def __init__(self, nodes):
        self.nodes = nodes

    def getChildren(self):
        children = []
        children.extend(flatten(self.nodes))
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.extend(flatten_nodes(self.nodes))
        return tuple(nodelist)

    def __repr__(self):
        return "List(%s)" % (repr(self.nodes),)

class Yield(Node):
    nodes["yield"] = "Yield"
    def __init__(self, value):
        self.value = value

    def getChildren(self):
        return self.value,

    def getChildNodes(self):
        return self.value,

    def __repr__(self):
        return "Yield(%s)" % (repr(self.value),)

class LeftShift(Node):
    nodes["leftshift"] = "LeftShift"
    def __init__(self, (left, right)):
        self.left = left
        self.right = right

    def getChildren(self):
        return self.left, self.right

    def getChildNodes(self):
        return self.left, self.right

    def __repr__(self):
        return "LeftShift((%s, %s))" % (repr(self.left), repr(self.right))

class AssName(Node):
    nodes["assname"] = "AssName"
    def __init__(self, name, flags):
        self.name = name
        self.flags = flags

    def getChildren(self):
        return self.name, self.flags

    def getChildNodes(self):
        return ()

    def __repr__(self):
        return "AssName(%s, %s)" % (repr(self.name), repr(self.flags))

class While(Node):
    nodes["while"] = "While"
    def __init__(self, test, body, else_):
        self.test = test
        self.body = body
        self.else_ = else_

    def getChildren(self):
        children = []
        children.append(self.test)
        children.append(self.body)
        children.append(self.else_)
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.append(self.test)
        nodelist.append(self.body)
        if self.else_ is not None:            nodelist.append(self.else_)
        return tuple(nodelist)

    def __repr__(self):
        return "While(%s, %s, %s)" % (repr(self.test), repr(self.body), repr(self.else_))

class Continue(Node):
    nodes["continue"] = "Continue"
    def __init__(self, ):
        pass

    def getChildren(self):
        return ()

    def getChildNodes(self):
        return ()

    def __repr__(self):
        return "Continue()"

class Backquote(Node):
    nodes["backquote"] = "Backquote"
    def __init__(self, expr):
        self.expr = expr

    def getChildren(self):
        return self.expr,

    def getChildNodes(self):
        return self.expr,

    def __repr__(self):
        return "Backquote(%s)" % (repr(self.expr),)

class Discard(Node):
    nodes["discard"] = "Discard"
    def __init__(self, expr):
        self.expr = expr

    def getChildren(self):
        return self.expr,

    def getChildNodes(self):
        return self.expr,

    def __repr__(self):
        return "Discard(%s)" % (repr(self.expr),)

class Div(Node):
    nodes["div"] = "Div"
    def __init__(self, (left, right)):
        self.left = left
        self.right = right

    def getChildren(self):
        return self.left, self.right

    def getChildNodes(self):
        return self.left, self.right

    def __repr__(self):
        return "Div((%s, %s))" % (repr(self.left), repr(self.right))

class Assign(Node):
    nodes["assign"] = "Assign"
    def __init__(self, nodes, expr):
        self.nodes = nodes
        self.expr = expr

    def getChildren(self):
        children = []
        children.extend(flatten(self.nodes))
        children.append(self.expr)
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.extend(flatten_nodes(self.nodes))
        nodelist.append(self.expr)
        return tuple(nodelist)

    def __repr__(self):
        return "Assign(%s, %s)" % (repr(self.nodes), repr(self.expr))

class Lambda(Node):
    nodes["lambda"] = "Lambda"
    def __init__(self, argnames, defaults, flags, code):
        self.argnames = argnames
        self.defaults = defaults
        self.flags = flags
        self.code = code
        self.varargs = self.kwargs = None
        if flags & CO_VARARGS:
            self.varargs = 1
        if flags & CO_VARKEYWORDS:
            self.kwargs = 1


    def getChildren(self):
        children = []
        children.append(self.argnames)
        children.extend(flatten(self.defaults))
        children.append(self.flags)
        children.append(self.code)
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.extend(flatten_nodes(self.defaults))
        nodelist.append(self.code)
        return tuple(nodelist)

    def __repr__(self):
        return "Lambda(%s, %s, %s, %s)" % (repr(self.argnames), repr(self.defaults), repr(self.flags), repr(self.code))

class And(Node):
    nodes["and"] = "And"
    def __init__(self, nodes):
        self.nodes = nodes

    def getChildren(self):
        children = []
        children.extend(flatten(self.nodes))
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.extend(flatten_nodes(self.nodes))
        return tuple(nodelist)

    def __repr__(self):
        return "And(%s)" % (repr(self.nodes),)

class Compare(Node):
    nodes["compare"] = "Compare"
    def __init__(self, expr, ops):
        self.expr = expr
        self.ops = ops

    def getChildren(self):
        children = []
        children.append(self.expr)
        children.extend(flatten(self.ops))
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.append(self.expr)
        nodelist.extend(flatten_nodes(self.ops))
        return tuple(nodelist)

    def __repr__(self):
        return "Compare(%s, %s)" % (repr(self.expr), repr(self.ops))

class Bitor(Node):
    nodes["bitor"] = "Bitor"
    def __init__(self, nodes):
        self.nodes = nodes

    def getChildren(self):
        children = []
        children.extend(flatten(self.nodes))
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.extend(flatten_nodes(self.nodes))
        return tuple(nodelist)

    def __repr__(self):
        return "Bitor(%s)" % (repr(self.nodes),)

class Bitxor(Node):
    nodes["bitxor"] = "Bitxor"
    def __init__(self, nodes):
        self.nodes = nodes

    def getChildren(self):
        children = []
        children.extend(flatten(self.nodes))
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.extend(flatten_nodes(self.nodes))
        return tuple(nodelist)

    def __repr__(self):
        return "Bitxor(%s)" % (repr(self.nodes),)

class CallFunc(Node):
    nodes["callfunc"] = "CallFunc"
    def __init__(self, node, args, star_args = None, dstar_args = None):
        self.node = node
        self.args = args
        self.star_args = star_args
        self.dstar_args = dstar_args

    def getChildren(self):
        children = []
        children.append(self.node)
        children.extend(flatten(self.args))
        children.append(self.star_args)
        children.append(self.dstar_args)
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.append(self.node)
        nodelist.extend(flatten_nodes(self.args))
        if self.star_args is not None:            nodelist.append(self.star_args)
        if self.dstar_args is not None:            nodelist.append(self.dstar_args)
        return tuple(nodelist)

    def __repr__(self):
        return "CallFunc(%s, %s, %s, %s)" % (repr(self.node), repr(self.args), repr(self.star_args), repr(self.dstar_args))

class Global(Node):
    nodes["global"] = "Global"
    def __init__(self, names):
        self.names = names

    def getChildren(self):
        return self.names,

    def getChildNodes(self):
        return ()

    def __repr__(self):
        return "Global(%s)" % (repr(self.names),)

class Add(Node):
    nodes["add"] = "Add"
    def __init__(self, (left, right)):
        self.left = left
        self.right = right

    def getChildren(self):
        return self.left, self.right

    def getChildNodes(self):
        return self.left, self.right

    def __repr__(self):
        return "Add((%s, %s))" % (repr(self.left), repr(self.right))

class ListCompIf(Node):
    nodes["listcompif"] = "ListCompIf"
    def __init__(self, test):
        self.test = test

    def getChildren(self):
        return self.test,

    def getChildNodes(self):
        return self.test,

    def __repr__(self):
        return "ListCompIf(%s)" % (repr(self.test),)

class Sub(Node):
    nodes["sub"] = "Sub"
    def __init__(self, (left, right)):
        self.left = left
        self.right = right

    def getChildren(self):
        return self.left, self.right

    def getChildNodes(self):
        return self.left, self.right

    def __repr__(self):
        return "Sub((%s, %s))" % (repr(self.left), repr(self.right))

class Pass(Node):
    nodes["pass"] = "Pass"
    def __init__(self, ):
        pass

    def getChildren(self):
        return ()

    def getChildNodes(self):
        return ()

    def __repr__(self):
        return "Pass()"

class UnarySub(Node):
    nodes["unarysub"] = "UnarySub"
    def __init__(self, expr):
        self.expr = expr

    def getChildren(self):
        return self.expr,

    def getChildNodes(self):
        return self.expr,

    def __repr__(self):
        return "UnarySub(%s)" % (repr(self.expr),)

class If(Node):
    nodes["if"] = "If"
    def __init__(self, tests, else_):
        self.tests = tests
        self.else_ = else_

    def getChildren(self):
        children = []
        children.extend(flatten(self.tests))
        children.append(self.else_)
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.extend(flatten_nodes(self.tests))
        if self.else_ is not None:            nodelist.append(self.else_)
        return tuple(nodelist)

    def __repr__(self):
        return "If(%s, %s)" % (repr(self.tests), repr(self.else_))

class ListComp(Node):
    nodes["listcomp"] = "ListComp"
    def __init__(self, expr, quals):
        self.expr = expr
        self.quals = quals

    def getChildren(self):
        children = []
        children.append(self.expr)
        children.extend(flatten(self.quals))
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.append(self.expr)
        nodelist.extend(flatten_nodes(self.quals))
        return tuple(nodelist)

    def __repr__(self):
        return "ListComp(%s, %s)" % (repr(self.expr), repr(self.quals))

class ListCompFor(Node):
    nodes["listcompfor"] = "ListCompFor"
    def __init__(self, assign, list, ifs):
        self.assign = assign
        self.list = list
        self.ifs = ifs

    def getChildren(self):
        children = []
        children.append(self.assign)
        children.append(self.list)
        children.extend(flatten(self.ifs))
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.append(self.assign)
        nodelist.append(self.list)
        nodelist.extend(flatten_nodes(self.ifs))
        return tuple(nodelist)

    def __repr__(self):
        return "ListCompFor(%s, %s, %s)" % (repr(self.assign), repr(self.list), repr(self.ifs))

class GenExpr(Node):
    nodes["genexpr"] = "GenExpr"
    def __init__(self, code):
        self.code = code
        self.argnames = ['[outmost-iterable]']
        self.varargs = self.kwargs = None

    def getChildren(self):
        return self.code,

    def getChildNodes(self):
        return self.code,

    def __repr__(self):
        return "GenExpr(%s)" % (repr(self.code),)

class GenExprInner(Node):
    nodes["genexprinner"] = "GenExprInner"
    def __init__(self, expr, quals):
        self.expr = expr
        self.quals = quals

    def getChildren(self):
        children = []
        children.append(self.expr)
        children.extend(flatten(self.quals))
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.append(self.expr)
        nodelist.extend(flatten_nodes(self.quals))
        return tuple(nodelist)

    def __repr__(self):
        return "GenExprInner(%s, %s)" % (repr(self.expr), repr(self.quals))

class GenExprFor(Node):
    nodes["genexprfor"] = "GenExprFor"
    def __init__(self, assign, iter, ifs):
        self.assign = assign
        self.iter = iter
        self.ifs = ifs
        self.is_outmost = False

    def getChildren(self):
        children = []
        children.append(self.assign)
        children.append(self.iter)
        children.extend(flatten(self.ifs))
        return tuple(children)

    def getChildNodes(self):
        nodelist = []
        nodelist.append(self.assign)
        nodelist.append(self.iter)
        nodelist.extend(flatten_nodes(self.ifs))
        return tuple(nodelist)

    def __repr__(self):
        return "GenExprFor(%s, %s, %s)" % (repr(self.assign), repr(self.iter), repr(self.ifs))

class GenExprIf(Node):
    nodes["genexprif"] = "GenExprIf"
    def __init__(self, test):
        self.test = test

    def getChildren(self):
        return self.test,

    def getChildNodes(self):
        return self.test,

    def __repr__(self):
        return "GenExprIf(%s)" % (repr(self.test),)

klasses = globals()
for k in nodes.keys():
    nodes[k] = klasses[nodes[k]]
