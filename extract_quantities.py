import ifcopenshell
import os

def calculate_volume_from_geometry(element):
    """
    Tenta acessar a representação geométrica do elemento (IfcShapeRepresentation) 
    para estimar o volume.
    """
    try:
        if element.Representation:
            shape = element.Representation.Representations
            for rep in shape:
                if rep.RepresentationType == "SweptSolid":
                    # Apenas representações SweptSolid possuem volumes fáceis de calcular
                    return rep.RepresentationIdentifier  # Ajustar para cálculo real se possível
    except Exception as e:
        print(f"Erro ao acessar geometria: {e}")
    return 0  # Retorna 0 se o volume não for calculado

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

        # Gerar relatórios como antes
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        report_path = f"{base_name}_geometry_report.txt"
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
            extract_volumes_with_geometry(file)

if __name__ == "__main__":
    process_all_ifc_files()
