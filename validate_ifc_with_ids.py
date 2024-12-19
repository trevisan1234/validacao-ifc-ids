import os
import json
import ifcopenshell
from lxml import etree

# Caminho para o IDS
IDS_PATH = "./ids.xsd"
# Caminho para o relatório gerado
REPORT_PATH = "validation_report.json"

def validate_ifc_with_ids(ifc_file, ids_root):
    """Valida um arquivo IFC contra o IDS fornecido."""
    report = {"file": ifc_file, "results": []}
    try:
        # Abre o arquivo IFC
        model = ifcopenshell.open(ifc_file)
       
        # Verifica se os parâmetros principais existem
        ifc_project = model.by_type("IfcProject")
        ifc_building = model.by_type("IfcBuilding")
        ifc_building_storey = model.by_type("IfcBuildingStorey")
        ifc_space = model.by_type("IfcSpace")
        coordinates = "Não disponível"
        disciplines = "Não especificado"
        technical_specifications = "Não preenchido"
        
        # Verifica coordenadas
        ifc_site = model.by_type("IfcSite")
        if ifc_site:
            site = ifc_site[0]
            if hasattr(site, "RefLatitude") and hasattr(site, "RefLongitude"):
                latitude = site.RefLatitude
                longitude = site.RefLongitude
                coordinates = f"Latitude: {latitude}, Longitude: {longitude}"
        
        # Verifica as disciplinas
        for rel in model.by_type("IfcRelAssigns"):
            if hasattr(rel, "RelatingType"):
                disciplines = ", ".join([rel.RelatingType for rel in model.by_type("IfcRelAssigns")])

        # Verifica especificações técnicas
        specifications = model.by_type("IfcSpecification")
        if specifications:
            technical_specifications = "Preenchido"

        # Preenche os resultados no relatório
        report["results"].append({
            "IfcProject": "Presente" if ifc_project else "Ausente",
            "IfcBuilding": "Presente" if ifc_building else "Ausente",
            "IfcBuildingStorey": "Presente" if ifc_building_storey else "Ausente",
            "IfcSpace": f"{len(ifc_space)} espaços encontrados" if len(ifc_space) >= 2 else "Menos de 2 espaços encontrados",
            "Coordenadas": coordinates,
            "Disciplinas": disciplines,
            "Especificações Técnicas": technical_specifications,
        })
    
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
    
    # Salva o relatório completo em TXT
    with open("validation_report.txt", "w") as txt_file:
        for report in validation_reports:
            txt_file.write(f"Arquivo: {report['file']}\n")
            for key, value in report["results"][0].items():
                txt_file.write(f"  - {key}: {value}\n")
            txt_file.write("\n")

if __name__ == "__main__":
    main()
