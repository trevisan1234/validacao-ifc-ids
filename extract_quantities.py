import ifcopenshell

def extract_volume_from_ifc(file_path):
    """
    Extrai o volume de elementos especificados (IfcBeam, IfcColumn, IfcSlab, IfcPile) em um arquivo IFC.
    """
    try:
        # Carregar o arquivo IFC
        ifc_file = ifcopenshell.open(file_path)
        
        # Elementos a serem analisados
        elements_to_check = ["IfcBeam", "IfcColumn", "IfcSlab", "IfcPile"]
        total_volume = 0.0

        # Iterar pelos tipos de elementos
        for element_type in elements_to_check:
            elements = ifc_file.by_type(element_type)
            for element in elements:
                # Obter a propriedade de volume
                if element.HasQuantities:
                    for quantity in element.HasQuantities:
                        if quantity.is_a("IfcQuantityVolume"):
                            total_volume += quantity.VolumeValue

        # Exibir o total
        print(f"Volume total de concreto armado (m³): {total_volume:.2f}")
        
        # Salvar relatório
        with open("quantities_report.txt", "w") as report:
            report.write(f"Volume total de concreto armado (m³): {total_volume:.2f}\n")

    except Exception as e:
        print(f"Erro ao processar o arquivo IFC: {e}")

# Caminho para o arquivo IFC (atualize conforme necessário)
if __name__ == "__main__":
    file_path = "seu_arquivo.ifc"  # Substitua pelo caminho do seu arquivo IFC
    extract_volume_from_ifc(file_path)
