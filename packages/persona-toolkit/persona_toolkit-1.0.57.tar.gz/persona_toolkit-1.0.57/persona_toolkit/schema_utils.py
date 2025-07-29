import inspect
from copy import deepcopy
from typing import get_args, get_origin, Union

from pydantic import BaseModel


def collect_referenced_models(model: type[BaseModel]) -> set[type[BaseModel]]:
    visited = set()

    def _collect(model_cls):
        if model_cls in visited or not inspect.isclass(model_cls):
            return
        if not issubclass(model_cls, BaseModel):
            return
        visited.add(model_cls)

        for field in model_cls.model_fields.values():
            field_type = field.annotation
            origin = get_origin(field_type)
            args = get_args(field_type)

            if inspect.isclass(field_type) and issubclass(field_type, BaseModel):
                _collect(field_type)
            elif origin in (list, tuple, set, dict, Union):
                for arg in args:
                    if inspect.isclass(arg) and issubclass(arg, BaseModel):
                        _collect(arg)

    _collect(model)
    return visited


def flatten_schema(model: type[BaseModel]) -> dict:
    """
    Generate a flattened JSON schema for the given model only,
    resolving any $ref that appear in that model's schema.
    If a property contains 'anyOf', extract its types and mark it as not required.
    """
    full_schema = model.model_json_schema(ref_template="#/$defs/{model}")
    schema_fragment = deepcopy(full_schema)

    # Colleziona i modelli referenziati solo da questo schema
    ref_names_in_schema = set()

    def _collect_ref_names(node):
        if isinstance(node, dict):
            if "$ref" in node:
                ref_path = node["$ref"]
                if ref_path.startswith("#/$defs/"):
                    ref_name = ref_path.split("/")[-1]
                    ref_names_in_schema.add(ref_name)
            for v in node.values():
                _collect_ref_names(v)
        elif isinstance(node, list):
            for item in node:
                _collect_ref_names(item)

    _collect_ref_names(schema_fragment)

    # Prende solo i modelli referenziati nel ref_names_in_schema
    ref_models = {
        name: cls for cls in collect_referenced_models(model)
        if (name := cls.__name__) in ref_names_in_schema
    }

    ref_schemas = {
        name: m.model_json_schema(ref_template="#/$defs/{model}")
        for name, m in ref_models.items()
    }

    def _resolve_refs(node):
        if isinstance(node, dict):
            if "$ref" in node:
                ref_path = node["$ref"]
                if ref_path.startswith("#/$defs/"):
                    ref_name = ref_path.split("/")[-1]
                    if ref_name not in ref_schemas:
                        raise ValueError(f"Modello '{ref_name}' non trovato")
                    return _resolve_refs(ref_schemas[ref_name])
            return {k: _resolve_refs(v) for k, v in node.items()}
        elif isinstance(node, list):
            return [_resolve_refs(item) for item in node]
        else:
            return node

    flat_schema = _resolve_refs(schema_fragment)

    def _strip_defs(node):
        if isinstance(node, dict):
            return {
                k: _strip_defs(v)
                for k, v in node.items()
                if k != "$defs"
            }
        elif isinstance(node, list):
            return [_strip_defs(item) for item in node]
        else:
            return node

    flat_schema = _strip_defs(flat_schema)

    # --- Gestisci le proprietà 'anyOf': usa il primo tipo disponibile ma preserva i dati originali ---
    if "properties" in flat_schema:
        properties = flat_schema["properties"]
        required = set(flat_schema.get("required", []))
        for prop, prop_schema in properties.items():
            if "anyOf" in prop_schema and isinstance(prop_schema["anyOf"], list) and prop_schema["anyOf"]:
                first_type_schema = prop_schema["anyOf"][0]
                # Unisci il primo tipo con i dati originali, senza sovrascrivere le chiavi già presenti
                merged_schema = {**first_type_schema, **{k: v for k, v in prop_schema.items() if k != "anyOf"}}
                properties[prop] = merged_schema
                required.discard(prop)
        flat_schema["required"] = list(required)

    return flat_schema
