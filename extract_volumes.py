import ifcopenshell
import os

# Função para calcular o volume de um elemento
def calculate_volume(element):
    if hasattr(element, "Volume"):
        return element.Volume
    else:
        return 0

# Função para processar um arquivo IFC e extrair os volumes
def process_ifc_file(file_path):
    ifc_file = ifcopenshell.open(file_path)
    volume_summary = {
        "IfcBeam": 0,
        "IfcColumn": 0,
        "IfcSlab": 0,
        "IfcPile": 0
    }

    for element_type in volume_summary.keys():
        elements = ifc_file.by_type(element_type)
        for element in elements:
            volume_summary[element_type] += calculate_volume(element)

    return volume_summary

# Função para processar todos os arquivos IFC no diretório raiz
def process_all_ifc_files(directory):
    summary = {
        "IfcBeam": 0,
        "IfcColumn": 0,
        "IfcSlab": 0,
        "IfcPile": 0
    }

    for filename in os.listdir(directory):
        if filename.endswith(".ifc"):
            file_path = os.path.join(directory, filename)
            file_summary = process_ifc_file(file_path)
            for key in summary:
                summary[key] += file_summary[key]

    return summary

# Diretório raiz onde os arquivos IFC estão localizados
directory = "./"

# Processar todos os arquivos IFC e obter o resumo dos volumes
volume_summary = process_all_ifc_files(directory)

# Gerar o relatório
for element_type, volume in volume_summary.items():
    print(f"Total volume of {element_type}: {volume:.2f} m3")
