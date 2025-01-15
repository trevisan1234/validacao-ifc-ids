import ifcopenshell
import json
import csv
import os

def calculate_volume_alternative(element):
    """
    Calcula o volume de um elemento a partir de suas propriedades, caso disponível.
    Retorna o volume em metros cúbicos ou 0 se não for possível calcular.
    """
    try:
        # Verificar se o volume é uma propriedade definida no elemento
        for definition in element.IsDefinedBy:
            if definition.is_a("IfcRelDefinesByProperties"):
                property_set = definition.RelatingPropertyDefinition
                if property_set.is_a("IfcPropertySet"):
                    for property in property_set.HasProperties:
                        if property.is_a("IfcPropertySingleValue") and property.Name == "Volume":
                            return float(property.NominalValue.wrappedValue)
    except AttributeError:
        pass
    return 0  # Retorna 0 caso o cálculo não seja possível

def extract_volume_from_ifc(file_path):
    """
    Extrai o volume de elementos especificados (IfcBeam, IfcColumn, IfcSlab, IfcPile) de um arquivo IFC
    e gera relatórios nos formatos TXT, CSV e JSON.
    """
    try:
        print(f"Processando o arquivo IFC: {file_path}")
        ifc_file = ifcopenshell.open(file_path)
        elements_to_check = ["IfcBeam", "IfcColumn", "IfcSlab", "IfcPile"]
        total_volume = 0.0
        element_volumes = []

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
                    # Continuar para o cálculo alternativo
                    pass

                # Caso não tenha HasQuantities, calcular o volume usando propriedades
                if volume == 0:
                    volume = calculate_volume_alternative(element)

                total_volume += volume
                element_volumes.append({
                    "Element": element.GlobalId,
                    "Type": element_type,
                    "Volume_m3": volume
                })

        # Criar nomes de arquivo baseados no nome do arquivo IFC
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        txt_path = f"{base_name}_quantities_report.txt"
        csv_path = f"{base_name}_quantities_report.csv"
        json_path = f"{base_name}_quantities_report.json"

        # Relatório em TXT
        with open(txt_path, "w") as txt_file:
            txt_file.write(f"Arquivo analisado: {file_path}\n")
            txt_file.write(f"Volume total de concreto armado (m³): {total_volume:.2f}\n")
            txt_file.write("Detalhamento por elemento:\n")
            for entry in element_volumes:
                txt_file.write(f"{entry['Type']} (ID: {entry['Element']}): {entry['Volume_m3']:.2f} m³\n")

        # Relatório em CSV
        with open(csv_path, "w", newline="") as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=["Element", "Type", "Volume_m3"])
            csv_writer.writeheader()
            csv_writer.writerows(element_volumes)

        # Relatório em JSON
        with open(json_path, "w") as json_file:
            json.dump({
                "TotalVolume_m3": total_volume,
                "ElementDetails": element_volumes
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
