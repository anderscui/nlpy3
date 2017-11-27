# coding=utf-8
import json

import yaml

PARSE_API_DEF_FILE = 'apis.yaml'


# TODO: normalize properties of object type.


class BuiltinTypes(object):
    integer = 'integer'
    number = 'number'
    boolean = 'boolean'
    string = 'string'
    object = 'object'
    array = 'array'


class PropertyDef(object):
    def __init__(self, name, prop_type, is_array=False, default_val=None, prop_format=None):
        self.name = name
        self.prop_type = prop_type
        self.is_array = is_array
        self.default_val = default_val
        self.format = prop_format

    @staticmethod
    def parse(name, props):
        is_array = 'type' in props and props.get('type') == 'array'
        prop_type = get_type(props)
        default_val = props.get('default', None)
        prop_format = props.get('format', None)

        return PropertyDef(name, prop_type, is_array, default_val, prop_format)

    def is_scalar(self):
        return self.prop_type in {'integer', 'number', 'boolean', 'string'}

    def __str__(self):
        return 'Property: {name}, type: {prop_type}, is array： {array}, default: {default}, format: {format}'\
            .format(name=self.name,
                    prop_type=self.prop_type,
                    array='yes' if self.is_array else 'no',
                    default=self.default_val,
                    format=self.format if self.format else 'not set')


def load_resume_def():
    # TODO: validate types
    with open(PARSE_API_DEF_FILE, 'r') as f:
        apis = yaml.load(f)
    defs = apis['definitions']
    return defs


all_defs = load_resume_def()


def get_default_value(prop_def):
    prop_type = prop_def.prop_type
    if prop_def.default_val:
        return prop_def.default_val

    if prop_def.is_array:
        return []

    if prop_type == 'integer' or prop_type == 'number':
        return None
    elif prop_type == 'boolean':
        return None
    elif prop_type == 'string':
        return None
    elif prop_type == 'object':
        return {}
    else:
        # not array or object, it should be of unknown scalar type.
        return {}


def get_type(props):
    if 'type' in props:
        ptype = props.get('type')
        if ptype == 'array':
            return get_type(props['items'])
        else:
            return ptype
    ref = props.get('$ref')
    i = ref.rindex('/')
    return ref[i+1:]


def normalize_prop(obj, prop_defs, type_defs):
    # if this obj does not have properties (for scalar values)
    if not prop_defs:
        return obj

    for prop_name in prop_defs:
        sub_prop_def = PropertyDef.parse(prop_name, prop_defs[prop_name])

        # add default values for missing properties.
        if prop_name not in obj:
            obj[prop_name] = get_default_value(sub_prop_def)

        # normalize compound types
        prop = obj[prop_name]
        if sub_prop_def.is_scalar():
            pass
        else:
            sub_prop_defs = type_defs[sub_prop_def.prop_type]
            if sub_prop_def.is_array:
                for child in prop:
                    normalize_prop(child, sub_prop_defs, type_defs)
            else:
                normalize_prop(prop, sub_prop_defs, type_defs)
        # elif prop_type == 'object':
        #     pass


def normalize_missing_values(resume):
    type_defs = {d: v['properties'] for d, v in all_defs.items()}

    prop_defs = type_defs['resume']
    normalize_prop(resume, prop_defs, type_defs)
    return resume


if __name__ == '__main__':
    original = {'activities': [{}],
                'awards': [{}],
                'educations': [{}],
                'interns': [{}],
                'languages_set': [{}],
                'projects': [{}],
                'skills_set': [{}],
                'trainings': [{}],
                'works': [{}],
                'skills': ['python'],
                }
    normalized = normalize_missing_values(original)
    print(json.dumps(normalized, ensure_ascii=False, indent=2))
