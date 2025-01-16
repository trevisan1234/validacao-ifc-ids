import ifcopenshell
import os

def extract_volume_from_properties(element, total_volumes_by_type):
    """
    Extrai propriedades relacionadas ao volume (NetArea, Length) e acumula o volume no tipo do elemento.
    """
    try:
        net_area = None
        length = None

        # Itera pelos PropertySets associados ao elemento
        for definition in element.IsDefinedBy:
            if definition.is_a("IfcRelDefinesByProperties"):
                prop_set = definition.RelatingPropertyDefinition
                if prop_set.is_a("IfcPropertySet"):
                    for prop in prop_set.HasProperties:
                        if prop.is_a("IfcPropertySingleValue"):
                            if prop.Name == "NetArea":
                                net_area = prop.NominalValue.wrappedValue
                            elif prop.Name == "Length":
                                length = prop.NominalValue.wrappedValue

        # Calcula o volume estimado, se possível
        if net_area is not None and length is not None:
            estimated_volume = net_area * length
            element_type = element.is_a()
            total_volumes_by_type[element_type] += estimated_volume

    except Exception as e:
        print(f"Erro ao acessar propriedades do elemento ID {element.id()}: {e}")


def process_file(file_path):
    """
    Processa um arquivo IFC, calcula volumes por tipo de elemento e gera um relatório.
    """
    try:
        ifc_file = ifcopenshell.open(file_path)
        total_volumes_by_type = {"IfcBeam": 0.0, "IfcColumn": 0.0, "IfcSlab": 0.0, "IfcPile": 0.0}
        elements_to_check = list(total_volumes_by_type.keys())

        for element_type in elements_to_check:
            elements = ifc_file.by_type(element_type)
            for element in elements:
                extract_volume_from_properties(element, total_volumes_by_type)

        # Gera o relatório consolidado
        report_file = f"{os.path.splitext(file_path)[0]}_volumes_report.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(f"Arquivo analisado: {file_path}\n")
            f.write("Volumes totais por tipo de elemento (m³):\n")
            for element_type, total_volume in total_volumes_by_type.items():
                f.write(f"{element_type}: {total_volume:.2f} m³\n")
        print(f"Relatório gerado: {report_file}")

    except Exception as e:
        print(f"Erro ao processar o arquivo {file_path}: {e}")


# Processar todos os arquivos na pasta
def process_all_ifc_files():
    for file in os.listdir("."):
        if file.endswith(".ifc"):
            process_file(file)


if __name__ == "__main__":
    process_all_ifc_files()
