import ifcopenshell
import os

def extract_volume_from_properties(element):
    """
    Registra detalhes completos de todas as propriedades disponíveis
    nos PropertySets associados ao elemento.
    """
    try:
        print(f"Elemento ID {element.id()} está sendo processado...")
        for definition in element.IsDefinedBy:
            if definition.is_a("IfcRelDefinesByProperties"):
                prop_set = definition.RelatingPropertyDefinition
                if prop_set.is_a("IfcPropertySet"):
                    print(f"Elemento ID {element.id()} possui PropertySet: {prop_set.Name}")
                    for prop in prop_set.HasProperties:
                        if prop.is_a("IfcPropertySingleValue"):
                            print(f" - Propriedade: {prop.Name}, Tipo: {prop.NominalValue.get_attribute('type')}, Valor: {prop.NominalValue}")
                        else:
                            print(f" - Propriedade desconhecida: {prop.Name}, Tipo: {type(prop)}")
    except Exception as e:
        print(f"Erro ao acessar propriedades do elemento ID {element.id()}: {e}")

def process_file(file_path):
    """
    Processa um arquivo IFC e registra informações completas dos elementos.
    """
    try:
        ifc_file = ifcopenshell.open(file_path)
        elements_to_check = ["IfcBeam", "IfcColumn", "IfcSlab", "IfcPile"]

        for element_type in elements_to_check:
            elements = ifc_file.by_type(element_type)
            print(f"Processando {len(elements)} elementos do tipo {element_type}.")
            for element in elements:
                extract_volume_from_properties(element)

    except Exception as e:
        print(f"Erro ao processar o arquivo {file_path}: {e}")

# Processar todos os arquivos na pasta
def process_all_ifc_files():
    for file in os.listdir("."):
        if file.endswith(".ifc"):
            process_file(file)

if __name__ == "__main__":
    process_all_ifc_files()
