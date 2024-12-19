import os
import json
import ifcopenshell
from lxml import etree

# Caminho para o IDS
IDS_PATH = "path/to/your/ids.xml"
# Caminho para o relatório gerado
REPORT_PATH = "validation_report.json"

def validate_ifc_with_ids(ifc_file, ids_root):
    """Valida um arquivo IFC contra o IDS fornecido."""
    report = {"file": ifc_file, "results": []}
    try:
        # Abre o arquivo IFC
        model = ifcopenshell.open(ifc_file)
        
        # Verifica cada requisito do IDS
        for entity in ids_root.findall(".//{https://standards.buildingsmart.org/IDS/1.0}Entity"):
            entity_name = entity.find("{https://standards.buildingsmart.org/IDS/1.0}Name").text
            requirement = {"entity": entity_name, "status": "FAILED"}
            
            # Procura entidades no modelo IFC
            if model.by_type(entity_name):
                requirement["status"] = "PASSED"
            
            # Adiciona ao relatório
            report["results"].append(requirement)
    except Exception as e:
        report["error"] = str(e)
    
    return report

def main():
    # Carrega o IDS
    with open(IDS_PATH, "r") as f:
        ids_root = etree.parse(f).getroot()

    # Valida todos os arquivos IFC no repositório
    validation_reports = []
    for file in os.listdir("."):
        if file.endswith(".ifc"):
            validation_reports.append(validate_ifc_with_ids(file, ids_root))

    # Salva o relatório completo
    with open(REPORT_PATH, "w") as report_file:
        json.dump(validation_reports, report_file, indent=4)

if __name__ == "__main__":
    main()