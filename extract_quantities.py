import ifcopenshell
import os

def extract_volume_from_properties(element, report_lines):
    """
    Extrai propriedades relacionadas ao volume (NetArea, Length) e registra no relatório.
    """
    try:
        report_lines.append(f"Elemento ID {element.id()} está sendo processado...")
        volumes = []
        for definition in element.IsDefinedBy:
            if definition.is_a("IfcRelDefinesByProperties"):
                prop_set = definition.RelatingPropertyDefinition
                if prop_set.is_a("IfcPropertySet"):
                    report_lines.append(f"Elemento ID {element.id()} possui PropertySet: {prop_set.Name}")
                    for prop in prop_set.HasProperties:
                        if prop.is_a("IfcPropertySingleValue"):
                            prop_name = prop.Name
                            prop_value = prop.NominalValue.wrappedValue if prop.NominalValue else "Sem valor"
                            report_lines.append(f" - Propriedade: {prop_name}, Valor: {prop_value}")

                            # Verifica propriedades relevantes
                            if prop_name in ["NetArea", "Length"]:
                                volumes.append(prop_value)

        # Se NetArea e Length forem encontrados, calcula o volume
        if len(volumes) == 2:
            estimated_volume = volumes[0] * volumes[1]
            report_lines.append(f"Volume estimado: {estimated_volume} m³ para o elemento ID {element.id()}")
            return estimated_volume
        else:
            report_lines.append(f"Volume não pôde ser estimado para o elemento ID {element.id()}.")

    except Exception as e:
        report_lines.append(f"Erro ao acessar propriedades do elemento ID {element.id()}: {e}")

    return 0  # Retorna 0 se o volume não for calculado


def process_file(file_path):
    """
    Processa um arquivo IFC, calcula volumes e gera um relatório.
    """
    try:
        ifc_file = ifcopenshell.open(file_path)
        report_lines = []
        elements_to_check = ["IfcBeam", "IfcColumn", "IfcSlab", "IfcPile"]

        for element_type in elements_to_check:
            elements = ifc_file.by_type(element_type)
            report_lines.append(f"Processando {len(elements)} elementos do tipo {element_type}.")
            for element in elements:
                extract_volume_from_properties(element, report_lines)

        # Gera o relatório
        report_file = f"{os.path.splitext(file_path)[0]}_properties_report.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("\n".join(report_lines))
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
