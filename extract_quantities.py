import ifcopenshell
import os

def extract_net_volume(element):
    """
    Tenta acessar o NetVolume do PropertySet BaseQuantities associado ao elemento.
    """
    try:
        for definition in element.IsDefinedBy:
            if definition.is_a("IfcRelDefinesByProperties"):
                prop_set = definition.RelatingPropertyDefinition
                if prop_set.is_a("IfcElementQuantity"):  # Verifica se é um conjunto de quantidades
                    for quantity in prop_set.Quantities:
                        if quantity.is_a("IfcQuantityVolume") and quantity.Name == "NetVolume":
                            return quantity.VolumeValue
    except Exception as e:
        print(f"Erro ao acessar NetVolume: {e}")
    return 0  # Retorna 0 se o NetVolume não for encontrado ou calculado

def extract_volumes_with_properties(file_path):
    try:
        ifc_file = ifcopenshell.open(file_path)
        elements_to_check = ["IfcBeam", "IfcColumn", "IfcSlab", "IfcPile"]
        total_volumes_by_type = {element_type: 0.0 for element_type in elements_to_check}

        for element_type in elements_to_check:
            elements = ifc_file.by_type(element_type)
            for element in elements:
                volume = extract_net_volume(element)
                total_volumes_by_type[element_type] += volume

        # Gerar relatórios como antes
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        report_path = f"{base_name}_properties_report.txt"
        with open(report_path, "w") as report_file:
            for element_type, total_volume in total_volumes_by_type.items():
                report_file.write(f"{element_type}: {total_volume:.2f} m³\n")

        print(f"Relatório gerado: {report_path}")
        return report_path

    except Exception as e:
        print(f"Erro ao processar o arquivo IFC: {e}")
        return None

# Processar todos os arquivos na pasta
def process_all_ifc_files():
    for file in os.listdir("."):
        if file.endswith(".ifc"):
            extract_volumes_with_properties(file)

if __name__ == "__main__":
    process_all_ifc_files()
