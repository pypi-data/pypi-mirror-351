"""
AST Node Predicate and Access Utilities for Pattern Matching and Traversal

This module provides utilities for accessing and matching AST nodes in a consistent way. It contains three primary
classes:

1. DOT: Provides consistent accessor methods for AST node attributes across different node types, simplifying the access
	to node properties.

2. be: Offers type-guard functions that verify AST node types, enabling safe type narrowing for static type checking and
	improving code safety.

3. ifThis: Contains predicate functions for matching AST nodes based on various criteria, enabling precise targeting of
	nodes for analysis or transformation.

These utilities form the foundation of the pattern-matching component in the AST manipulation framework, working in
conjunction with the NodeChanger and NodeTourist classes to enable precise and targeted code transformations. Together,
they implement a declarative approach to AST manipulation that separates node identification (ifThis), type verification
(be), and data access (DOT).
"""

from collections.abc import Callable
from astToolkit import Be, DOT
from typing import Any, TypeGuard, cast
import ast

class IfThis:
	"""
	Provide predicate functions for matching and filtering AST nodes based on various criteria.

	The ifThis class contains static methods that generate predicate functions used to test whether AST nodes match
	specific criteria. These predicates can be used with NodeChanger and NodeTourist to identify and process specific
	patterns in the AST.

	The class provides predicates for matching various node types, attributes, identifiers, and structural patterns,
	enabling precise targeting of AST elements for analysis or transformation.
	"""
	@staticmethod
	def is_argIdentifier(identifier: str) -> Callable[[ast.AST], TypeGuard[ast.arg] | bool]:
		"""see also `isArgumentIdentifier`"""
		return lambda node: Be.arg(node) and IfThis.isIdentifier(identifier)(DOT.arg(node))
	@staticmethod
	def is_keywordIdentifier(identifier: str) -> Callable[[ast.AST], TypeGuard[ast.keyword] | bool]:
		"""see also `isArgumentIdentifier`"""
		return lambda node: Be.keyword(node) and node.arg is not None and IfThis.isIdentifier(identifier)(node.arg)

	@staticmethod
	def isArgumentIdentifier(identifier: str) -> Callable[[ast.AST], TypeGuard[ast.arg | ast.keyword] | bool]:
		return lambda node: (Be.arg(node) or Be.keyword(node)) and node.arg is not None and IfThis.isIdentifier(identifier)(node.arg)

	@staticmethod
	def isAssignAndTargets0Is(targets0Predicate: Callable[[ast.AST], bool]) -> Callable[[ast.AST], TypeGuard[ast.AnnAssign] | bool]:
		""" `node` is `ast.Assign` and `node.targets[0]` matches `targets0Predicate`."""
		return lambda node: Be.Assign(node) and targets0Predicate(node.targets[0])

	@staticmethod
	def isAttributeIdentifier(identifier: str) -> Callable[[ast.AST], TypeGuard[ast.Attribute] | bool]:
		""" 1. `node` is `ast.Attribute`,
			2. zero or more direct descendants in an unbroken chain are `ast.Attribute`, `ast.Subscript`, or `ast.Starred`,
			3. the direct descendant chain ends with `ast.Name`, and
			4. the `ast.Name` `id` attribute is `identifier`."""
		def workhorse(node: ast.AST) -> TypeGuard[ast.Attribute]:
			return Be.Attribute(node) and IfThis.isNestedNameIdentifier(identifier)(DOT.value(node))
		return workhorse

	@staticmethod
	def isAttributeName(node: ast.AST) -> TypeGuard[ast.Attribute]:
		""" Displayed as Name.attribute."""
		return Be.Attribute(node) and Be.Name(DOT.value(node))

	@staticmethod
	def isAttributeNamespaceIdentifier(namespace: str, identifier: str) -> Callable[[ast.AST], TypeGuard[ast.Attribute] | bool]:
		return lambda node: IfThis.isAttributeName(node) and IfThis.isNameIdentifier(namespace)(DOT.value(node)) and IfThis.isIdentifier(identifier)(DOT.attr(node))

	@staticmethod
	def isCallIdentifier(identifier: str) -> Callable[[ast.AST], TypeGuard[ast.Call] | bool]:
		def workhorse(node: ast.AST) -> TypeGuard[ast.Call] | bool:
			return IfThis.isCallToName(node) and IfThis.isIdentifier(identifier)(DOT.id(cast(ast.Name, DOT.func(node))))
		return workhorse

	@staticmethod
	def isCallAttributeNamespaceIdentifier(namespace: str, identifier: str) -> Callable[[ast.AST], TypeGuard[ast.Call] | bool]:
		def workhorse(node: ast.AST) -> TypeGuard[ast.Call] | bool:
			return Be.Call(node) and IfThis.isAttributeNamespaceIdentifier(namespace, identifier)(DOT.func(node))
		return workhorse

	@staticmethod
	def isCallToName(node: ast.AST) -> TypeGuard[ast.Call]:
		return Be.Call(node) and Be.Name(DOT.func(node))

	@staticmethod
	def isClassDefIdentifier(identifier: str) -> Callable[[ast.AST], TypeGuard[ast.ClassDef] | bool]:
		return lambda node: Be.ClassDef(node) and IfThis.isIdentifier(identifier)(DOT.name(node))

	@staticmethod
	def isConstant_value(value: Any) -> Callable[[ast.AST], TypeGuard[ast.Constant] | bool]:
		return lambda node: Be.Constant(node) and DOT.value(node) == value

	@staticmethod
	def isFunctionDefIdentifier(identifier: str) -> Callable[[ast.AST], TypeGuard[ast.FunctionDef] | bool]:
		return lambda node: Be.FunctionDef(node) and IfThis.isIdentifier(identifier)(DOT.name(node))

	@staticmethod
	def isIdentifier(identifier: str) -> Callable[[str], TypeGuard[str] | bool]:
		return lambda node: node == identifier

	@staticmethod
	def isIfUnaryNotAttributeNamespaceIdentifier(namespace: str, identifier: str) -> Callable[[ast.AST], TypeGuard[ast.If] | bool]:
		return lambda node: (Be.If(node)
					and IfThis.isUnaryNotAttributeNamespaceIdentifier(namespace, identifier)(node.test))

	@staticmethod
	def isNameIdentifier(identifier: str) -> Callable[[ast.AST], TypeGuard[ast.Name] | bool]:
		return lambda node: Be.Name(node) and IfThis.isIdentifier(identifier)(DOT.id(node))

	@staticmethod
	def isNestedNameIdentifier(identifier: str) -> Callable[[ast.AST], TypeGuard[ast.Attribute | ast.Starred | ast.Subscript] | bool]:
		""" `node` is `ast.Name`

			OR

			1. `node` is one of `ast.Attribute`, `ast.Subscript`, or `ast.Starred`,
			2. zero or more direct descendants in an unbroken chain are `ast.Attribute`, `ast.Subscript`, or `ast.Starred`,
			3. the direct descendant chain ends with `ast.Name`,

			and

			The `ast.Name` `id` attribute is `identifier`."""
		def workhorse(node: ast.AST) -> TypeGuard[ast.Attribute | ast.Starred | ast.Subscript] | bool:
			return IfThis.isNameIdentifier(identifier)(node) or IfThis.isAttributeIdentifier(identifier)(node) or IfThis.isSubscriptIdentifier(identifier)(node) or IfThis.isStarredIdentifier(identifier)(node)
		return workhorse

	@staticmethod
	def isStarredIdentifier(identifier: str) -> Callable[[ast.AST], TypeGuard[ast.Starred] | bool]:
		""" 1. `node` is `ast.Starred`,
			2. zero or more direct descendants in an unbroken chain are `ast.Attribute`, `ast.Subscript`, or `ast.Starred`,
			3. the direct descendant chain ends with `ast.Name`, and
			4. the `ast.Name` `id` attribute is `identifier`."""
		def workhorse(node: ast.AST) -> TypeGuard[ast.Starred]:
			return Be.Starred(node) and IfThis.isNestedNameIdentifier(identifier)(DOT.value(node))
		return workhorse
	@staticmethod
	def isSubscriptIdentifier(identifier: str) -> Callable[[ast.AST], TypeGuard[ast.Subscript] | bool]:
		""" 1. `node` is `ast.Subscript`,
			2. zero or more direct descendants in an unbroken chain are `ast.Attribute`, `ast.Subscript`, or `ast.Starred`,
			3. the direct descendant chain ends with `ast.Name`, and
			4. the `ast.Name` `id` attribute is `identifier`."""
		def workhorse(node: ast.AST) -> TypeGuard[ast.Subscript]:
			return Be.Subscript(node) and IfThis.isNestedNameIdentifier(identifier)(DOT.value(node))
		return workhorse

	@staticmethod
	def isUnaryNotAttributeNamespaceIdentifier(namespace: str, identifier: str) -> Callable[[ast.AST], TypeGuard[ast.UnaryOp] | bool]:
		return lambda node: (Be.UnaryOp(node)
					and Be.Not(node.op)
					and IfThis.isAttributeNamespaceIdentifier(namespace, identifier)(node.operand))

	@staticmethod
	def matchesMeButNotAnyDescendant(predicate: Callable[[ast.AST], bool]) -> Callable[[ast.AST], bool]:
		return lambda node: predicate(node) and IfThis.matchesNoDescendant(predicate)(node)
	@staticmethod
	def matchesNoDescendant(predicate: Callable[[ast.AST], bool]) -> Callable[[ast.AST], bool]:
		def workhorse(node: ast.AST) -> bool:
			for descendant in ast.walk(node):
				if descendant is not node and predicate(descendant):
					return False
			return True
		return workhorse

	@staticmethod
	def unparseIs(astAST: ast.AST) -> Callable[[ast.AST], bool]:
		def workhorse(node: ast.AST) -> bool:
			return ast.unparse(node) == ast.unparse(astAST)
		return workhorse
