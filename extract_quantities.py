import ifcopenshell
import os

def extract_net_volume(element):
    """
    Tenta acessar o NetVolume do PropertySet BaseQuantities associado ao elemento.
    """
    try:
        has_quantity = False  # Flag para verificar se encontrou um IfcElementQuantity
        for definition in element.IsDefinedBy:
            if definition.is_a("IfcRelDefinesByProperties"):
                prop_set = definition.RelatingPropertyDefinition
                if prop_set.is_a("IfcElementQuantity"):
                    has_quantity = True
                    print(f"Elemento ID {element.id()} possui IfcElementQuantity.")
                    for quantity in prop_set.Quantities:
                        print(f" - Nome da propriedade: {quantity.Name}")
                        if quantity.is_a("IfcQuantityVolume") and quantity.Name == "NetVolume":
                            print(f" - NetVolume encontrado: {quantity.VolumeValue} m³ para o elemento ID {element.id()}")
                            return quantity.VolumeValue
        if not has_quantity:
            print(f"Elemento ID {element.id()} não possui IfcElementQuantity.")
    except Exception as e:
        print(f"Erro ao acessar propriedades do elemento ID {element.id()}: {e}")
    return 0  # Retorna 0 se o NetVolume não for encontrado ou calculado

def extract_volume_from_properties(element):
    """
    Calcula o volume estimado de um elemento usando as propriedades NetArea e Length.
    """
    try:
        net_area = None
        length = None

        # Itera pelos PropertySets associados ao elemento
        for definition in element.IsDefinedBy:
            if definition.is_a("IfcRelDefinesByProperties"):
                prop_set = definition.RelatingPropertyDefinition
                if prop_set.is_a("IfcPropertySet"):
                    print(f"Elemento ID {element.id()} possui PropertySet: {prop_set.Name}")
                    for prop in prop_set.HasProperties:
                        if prop.is_a("IfcPropertySingleValue"):
                            if prop.Name == "NetArea":
                                net_area = prop.NominalValue.wrappedValue
                                print(f"NetArea encontrado: {net_area} m²")
                            elif prop.Name == "Length":
                                length = prop.NominalValue.wrappedValue
                                print(f"Length encontrado: {length} m")

        # Calcula o volume estimado, se possível
        if net_area is not None and length is not None:
            estimated_volume = net_area * length
            print(f"Volume estimado: {estimated_volume} m³ para o elemento ID {element.id()}")
            return estimated_volume

    except Exception as e:
        print(f"Erro ao acessar propriedades do elemento ID {element.id()}: {e}")
    return 0  # Retorna 0 se o volume não for calculado

# Processar todos os arquivos na pasta
def process_all_ifc_files():
    for file in os.listdir("."):
        if file.endswith(".ifc"):
            extract_volumes_with_properties(file)

if __name__ == "__main__":
    process_all_ifc_files()
