import ifcopenshell
import os

def calculate_volume_from_geometry(element):
    """
    Calcula o volume de um elemento usando sua representação geométrica.
    Retorna o volume em m³ ou 0 se não for possível calcular.
    """
    try:
        if element.Representation:
            for rep in element.Representation.Representations:
                if rep.RepresentationType == "SweptSolid":
                    geometry = rep.Items[0]
                    if hasattr(geometry, "Volume"):
                        return geometry.Volume / 1_000_000  # Converte de mm³ para m³
    except Exception as e:
        print(f"Erro ao calcular volume para elemento {element.id()}: {e}")
    return 0  # Retorna 0 caso não seja possível calcular o volume

def extract_volumes_with_geometry(file_path):
    try:
        ifc_file = ifcopenshell.open(file_path)
        elements_to_check = ["IfcBeam", "IfcColumn", "IfcSlab", "IfcPile"]
        total_volumes_by_type = {element_type: 0.0 for element_type in elements_to_check}

        for element_type in elements_to_check:
            elements = ifc_file.by_type(element_type)
            for element in elements:
                volume = calculate_volume_from_geometry(element)
                total_volumes_by_type[element_type] += volume

        # Gerar relatórios diretamente para o console
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        print(f"Arquivo analisado: {base_name}")
        print("Volumes totais por tipo de elemento (m³):")
        for element_type, total_volume in total_volumes_by_type.items():
            print(f"{element_type}: {total_volume:.2f} m³")

        # Salvar relatório como arquivo TXT para upload como artifact
        report_name = f"{base_name}_volumes_report.txt"
        with open(report_name, "w") as report_file:
            report_file.write(f"Arquivo analisado: {base_name}\n")
            report_file.write("Volumes totais por tipo de elemento (m³):\n")
            for element_type, total_volume in total_volumes_by_type.items():
                report_file.write(f"{element_type}: {total_volume:.2f} m³\n")

        return report_name

    except Exception as e:
        print(f"Erro ao processar o arquivo IFC {file_path}: {e}")
        return None

# Processar todos os arquivos na pasta
def process_all_ifc_files():
    reports = []
    for file in os.listdir("."):
        if file.endswith(".ifc"):
            report = extract_volumes_with_geometry(file)
            if report:
                reports.append(report)
    return reports

if __name__ == "__main__":
    reports = process_all_ifc_files()
    if reports:
        print("Relatórios gerados com sucesso:")
        for report in reports:
            print(f"- {report}")
