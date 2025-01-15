import ifcopenshell
import ifcopenshell.util.element
import json
import csv
import os

def log_element_details(element):
    """
    Retorna uma string com detalhes básicos do elemento para depuração.
    """
    return f"ID: {element.GlobalId}, Name: {element.Name}, Type: {element.is_a()}"

def calculate_volume_alternative(element):
    """
    Calcula o volume de um elemento usando propriedades ou geometria.
    Retorna o volume em metros cúbicos ou 0 se não for possível calcular.
    """
    try:
        # Fallback 1: Propriedades (Volume em IfcPropertySet)
        for definition in element.IsDefinedBy:
            if definition.is_a("IfcRelDefinesByProperties"):
                property_set = definition.RelatingPropertyDefinition
                if property_set.is_a("IfcPropertySet"):
                    for property in property_set.HasProperties:
                        if property.is_a("IfcPropertySingleValue") and property.Name.lower() == "volume":
                            return float(property.NominalValue.wrappedValue)
    except AttributeError:
        pass

    try:
        # Fallback 2: Geometria (calculada pela função util.element.volume)
        return ifcopenshell.util.element.volume(element)
    except Excepti
