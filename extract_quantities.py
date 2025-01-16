import ifcopenshell
import os

def extract_volume_from_properties(element):
    """
    Calcula o volume estimado de um elemento usando as propriedades relevantes
    nos PropertySets associados.
    """
    try:
        net_area = None
        length = None
        volume = None

        # Itera pelos PropertySets associados ao elemento
        for definition in element.IsDefinedBy:
            if definition.is_a("IfcRelDefinesByProperties"):
                prop_set = definition.RelatingPropertyDefinition
                if prop_set.is_a("IfcPropertySet"):
                    print(f"Elemento ID {element.id()} possui PropertySet: {prop_set.Name}")
                    for prop in prop_set.HasProperties:
                        if prop.is_a("IfcPropertySingleValue"):
                            prop_name = prop.Name.lower()
                            if "area" in prop_name:
                                net_area = prop.NominalValue.wrappedValue
                                print(f"NetArea encontrado: {net_area} m²")
                            elif "length" in prop_name:
                                length = prop.NominalValue.wrappedValue
                                print(f"Length encontrado: {length} m")
                            elif "volume" in prop_name:
                                volume = prop.NominalValue.wrappedValue
                                print(f"Volume encontrado diretamente: {volume} m³")
        
        # Retorna o volume diretamente se encontrado
        if volume is not None:
            return volume

        # Caso contrário, calcula o volume estimado
        if net_area is not None and length is not None:
            estimated_volume = net_area * length
            print(f"Volume estimado: {estimated_volume} m³ para o elemento ID {element.id()}")
            return estimated_volume

    except Exception as e:
        print(f"Erro ao acessar propriedades do elemento ID {element.id()}: {e}")
    return 0  # Retorna 0 se o volume não for calculado

def process_file(file_path):
    """
    Processa um arquivo IFC e calcula os volumes de elementos relevantes.
    """
    try:
        ifc_file = ifcopenshell.open(file_path)
        elements_to_check = ["IfcBeam", "IfcColumn", "IfcSlab", "IfcPile"]
        total_volumes_by_type = {element_type: 0.0 for element_type in elements_to_check}

        for element_type in elements_to_check:
            elements = ifc_file.by_type(element_type)
            print(f"Processando {len(elements)} elementos do tipo {element_type}.")
            for element in elements:
                # Calcula o volume usando as propriedades disponíveis
                volume = extract_volume_from_properties(element)
                total_volumes_by_type[element_type] += volume

        # Gerar relatório
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        report_path = f"{base_name}_properties_report.txt"
        with open(report_path, "w") as report_file:
            for element_type, total_volume in total_volumes_by_type.items():
                report_file.write(f"{element_type}: {total_volume:.2f} m³\n")
        print(f"Relatório gerado: {report_path}")

    except Exception as e:
        print(f"Erro ao processar o arquivo {file_path}: {e}")

# Processar todos os arquivos na pasta
def process_all_ifc_files():
    for file in os.listdir("."):
        if file.endswith(".ifc"):
            process_file(file)

if __name__ == "__main__":
    process_all_ifc_files()
