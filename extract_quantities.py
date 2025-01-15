import ifcopenshell
import ifcopenshell.util.element
import json
import csv
import os

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
    except Exception:
        pass

    return 0  # Retorna 0 caso nenhuma alternativa funcione

def extract_volume_from_ifc(file_path):
    """
    Extrai o volume total por tipo de elemento (IfcBeam, IfcColumn, IfcSlab, IfcPile) de um arquivo IFC
    e gera relatórios nos formatos TXT, CSV e JSON.
    """
    try:
        print(f"Processando o arquivo IFC: {file_path}")
        ifc_file = ifcopenshell.open(file_path)
        elements_to_check = ["IfcBeam", "IfcColumn", "IfcSlab", "IfcPile"]
        total_volumes_by_type = {element_type: 0.0 for element_type in elements_to_check}

        for element_type in elements_to_check:
            elements = ifc_file.by_type(element_type)
            for element in elements:
                volume = 0
                # Tentar extrair o volume de HasQuantities
                try:
                    if element.HasQuantities:
                        for quantity in element.HasQuantities:
                            if quantity.is_a("IfcQuantityVolume"):
                                volume = quantity.VolumeValue
                                break
                except AttributeError:
                    pass

                # Usar cálculo alternativo, se necessário
                if volume == 0:
                    volume = calculate_volume_alternative(element)

                # Somar o volume total para o tipo de elemento
                total_volumes_by_type[element_type] += volume

        # Criar nomes de arquivo baseados no nome do arquivo IFC
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        txt_path = f"{base_name}_quantities_report.txt"
        csv_path = f"{base_name}_quantities_report.csv"
        json_path = f"{base_name}_quantities_report.json"

        # Relatório em TXT
        with open(txt_path, "w") as txt_file:
            txt_file.write(f"Arquivo analisado: {file_path}\n")
            txt_file.write("Volumes totais por tipo de elemento (m³):\n")
            for element_type, total_volume in total_volumes_by_type.items():
                txt_file.write(f"{element_type}: {total_volume:.2f} m³\n")

        # Relatório em CSV
        with open(csv_path, "w", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(["ElementType", "TotalVolume_m3"])
            for element_type, total_volume in total_volumes_by_type.items():
                csv_writer.writerow([element_type, total_volume])

        # Relatório em JSON
        with open(json_path, "w") as json_file:
            json.dump({
                "FileName": file_path,
                "TotalVolumesByType": total_volumes_by_type
            }, json_file, indent=4)

        print(f"Relatórios gerados para: {file_path}")
        return [txt_path, csv_path, json_path]

    except Exception as e:
        print(f"Erro ao processar o arquivo {file_path}: {e}")
        return []

def process_all_ifc_files():
    """
    Processa todos os arquivos IFC na pasta atual (raiz).
    """
    report_files = []
    for file in os.listdir("."):
        if file.endswith(".ifc"):
            reports = extract_volume_from_ifc(file)
            report_files.extend(reports)
    return report_files

if __name__ == "__main__":
    all_reports = process_all_ifc_files()
    print(f"Relatórios gerados: {all_reports}")
