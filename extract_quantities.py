import ifcopenshell
import json
import csv

def extract_volume_from_ifc(file_path):
    """
    Extrai o volume de elementos especificados (IfcBeam, IfcColumn, IfcSlab, IfcPile) em um arquivo IFC
    e gera relatórios nos formatos TXT, CSV e JSON.
    """
    try:
        # Carregar o arquivo IFC
        ifc_file = ifcopenshell.open(file_path)

        # Elementos a serem analisados
        elements_to_check = ["IfcBeam", "IfcColumn", "IfcSlab", "IfcPile"]
        total_volume = 0.0
        element_volumes = []

        # Iterar pelos tipos de elementos
        for element_type in elements_to_check:
            elements = ifc_file.by_type(element_type)
            for element in elements:
                if element.HasQuantities:
                    for quantity in element.HasQuantities:
                        if quantity.is_a("IfcQuantityVolume"):
                            volume = quantity.VolumeValue
                            total_volume += volume
                            element_volumes.append({
                                "Element": element.GlobalId,
                                "Type": element_type,
                                "Volume_m3": volume
                            })

        # Relatório em TXT
        txt_path = "quantities_report.txt"
        with open(txt_path, "w") as txt_file:
            txt_file.write(f"Volume total de concreto armado (m³): {total_volume:.2f}\n")
            txt_file.write("Detalhamento por elemento:\n")
            for entry in element_volumes:
                txt_file.write(f"{entry['Type']} (ID: {entry['Element']}): {entry['Volume_m3']:.2f} m³\n")

        # Relatório em CSV
        csv_path = "quantities_report.csv"
        with open(csv_path, "w", newline="") as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=["Element", "Type", "Volume_m3"])
            csv_writer.writeheader()
            csv_writer.writerows(element_volumes)

        # Relatório em JSON
        json_path = "quantities_report.json"
        with open(json_path, "w") as json_file:
            json.dump({
                "TotalVolume_m3": total_volume,
                "ElementDetails": element_volumes
            }, json_file, indent=4)

        print(f"Relatórios gerados com sucesso: {txt_path}, {csv_path}, {json_path}")

    except Exception as e:
        print(f"Erro ao processar o arquivo IFC: {e}")

# Caminho para o arquivo IFC (atualize conforme necessário)
if __name__ == "__main__":
    file_path = "seu_arquivo.ifc"  # Substitua pelo caminho do seu arquivo IFC
    extract_volume_from_ifc(file_path)
