# coding: utf-8
import json
from typing import Optional

class Parameter(object):
    def __init__(self, raw: dict):
        self.name = raw.get('Name', '')
        self.values = raw.get('Values', [])

    def encode(self) -> dict:
        return {
            'Name': self.name,
            'Values': self.values
        }

class BaseAction(object):
    def __init__(self, raw: dict):
        self.parameters = []
        for p in raw.get('Parameters', []):
            self.parameters.append(Parameter(p))

    def encode(self) -> dict:
        return {
            'Parameters': [p.encode() for p in self.parameters]
        }

    def set(self, name: str, values: list) -> None:
        for p in self.parameters:
            if p.name == name:
                p.values = values
                return
        self.parameters.append(Parameter({
            'Name': name,
            'Values': values
        }))

    def get(self, name: str) -> (Optional[Parameter], bool):
        for p in self.parameters:
            if p.name == name:
                return p, True
        return None, False


    def remove(self, name: str) -> None:
        for i, p in enumerate(self.parameters):
            if p.name == name:
                self.parameters.pop(i)
                return
        return

class ActionGroup(object):
    def __init__(self, raw: dict):
        self.dimension = raw.get('Dimension', '')
        self.group_parameters = []
        for a in raw.get('GroupParameters', []):
            self.group_parameters.append(BaseAction(a))

    def encode(self) -> dict:
        return {
            'Dimension': self.dimension,
            'GroupParameters': [g.encode() for g in self.group_parameters]
        }

class Action(object):
    def __init__(self, raw: dict):
        self.action = raw.get('Action', '')
        self.groups = []
        for g in raw.get('Groups', []):
            self.groups.append(ActionGroup(g))

    def encode(self) -> dict:
        return {
            'Action': self.action,
            'Groups': [g.encode() for g in self.groups]
        }

    def get_action_group(self, dimension: str) -> (Optional[ActionGroup], bool):
        for g in self.groups:
            if g.dimension == dimension:
                return g, True
        return None, False

    def set_action_group(self, dimension: str, group: ActionGroup):
        for i, g in enumerate(self.groups):
            if g.dimension == dimension:
                self.groups[i] = group
                return
        self.groups.append(group)

    def remove_action_group(self, dimension: str) -> None:
        for i, g in enumerate(self.groups):
            if g.dimension == dimension:
                self.groups.pop(i)
                return
        return

class BaseCondition(object):
    def __init__(self, raw: dict):
        self.object = raw.get('Object', '')
        self.name = raw.get('Name')
        self.operator = raw.get('Operator')
        self.ignore_case = raw.get('IgnoreCase')
        self.time_zone = raw.get('TimeZone')
        self.value = raw.get('Value')

    def encode(self) -> dict:
        data = {
            'Object': self.object
        }
        if self.name:
            data['Name'] = self.name
        if self.operator:
            data['Operator'] = self.operator
        if self.ignore_case is not None:
            data['IgnoreCase'] = self.ignore_case
        if self.time_zone :
            data['TimeZone'] = self.time_zone
        if self.value:
            data['Value'] = self.value
        return data


class Condition(object):
    def __init__(self, raw: dict):
        self.is_group = raw.get('IsGroup', False)
        self.connective = raw.get('Connective', 'and')
        self.condition_groups = []
        self.condition = BaseCondition(raw.get('Condition', {}))
        if self.is_group:
            for c in raw.get('ConditionGroups', []):
                self.condition_groups.append(Condition(c))

    def encode(self) -> dict:
        if self.is_group:
            return {
                'IsGroup': self.is_group,
                'Connective': self.connective,
                'ConditionGroups': [c.encode() for c in self.condition_groups]
            }
        else:
            return {
                'IsGroup': self.is_group,
                'Condition': self.condition.encode()
            }

class IfBlock(object):
    def __init__(self, raw: dict):
        self.condition = Condition(raw.get('Condition', {}))
        self.actions = [Action(a) for a in raw.get('Actions', [])]
        self.sub_rules = [Rule(r) for r in raw.get('SubRules', [])]

    def encode(self) -> dict:
        return {
            'Condition': self.condition.encode(),
            'Actions': [a.encode() for a in self.actions],
            'SubRules': [r.encode() for r in self.sub_rules]
        }


class ElseBlock(object):
    def __init__(self, raw: dict):
        self.actions = [Action(a) for a in raw.get('Actions', [])]
        self.sub_rules = [Rule(r) for r in raw.get('SubRules', [])]

    def encode(self) -> dict:
        return {
            'Actions': self.actions,
            'SubRules': [r.encode() for r in self.sub_rules]
        }


class Rule(object):
    def __init__(self, raw: Optional[dict] = None):
        if raw and isinstance(raw, dict):
            self.desc = raw.get('Desc', '')
            self.if_block = IfBlock(raw.get('IfBlock', {}))
            self.else_block = ElseBlock(raw.get('ElseBlock', {}))
        else:
            self.desc = ''
            self.if_block = IfBlock({})
            self.else_block = ElseBlock({})

    def encode(self) -> dict:
        return {
            'Desc': self.desc,
            'IfBlock': self.if_block.encode(),
            'ElseBlock': self.else_block.encode()
        }

    def encode_to_string(self) -> str:
        return json.dumps(self.encode())

    def decode_from_string(self, rule: str) -> None:
        rule = json.loads(rule)
        self.desc = rule.get('Desc', '')
        self.if_block = IfBlock(rule.get('IfBlock', {}))
        self.else_block = ElseBlock(rule.get('ElseBlock', {}))
