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

        # Verifica cada requisito do IDS
        for entity in ids_root.findall(".//{https://standards.buildingsmart.org/IDS/1.0}Entity"):
            entity_name = entity.find("{https://standards.buildingsmart.org/IDS/1.0}Name").text
            requirement = {"entity": entity_name, "status": "FAILED"}

            # Procura entidades no modelo IFC
            if model.by_type(entity_name):
                requirement["status"] = "PASSED"

            # Adiciona ao relatório
            report["results"].append(requirement)

        # Adiciona informações adicionais como coordenadas, disciplinas e outros
        ifc_project = model.by_type("IfcProject")
        ifc_building = model.by_type("IfcBuilding")
        ifc_storeys = model.by_type("IfcBuildingStorey")
        ifc_spaces = model.by_type("IfcSpace")
        ifc_site = model.by_type("IfcSite")

        # Verifica e armazena as coordenadas (Latitude e Longitude)
        coordinates = "Not available"
        if ifc_site:
            site = ifc_site[0]
            latitude = site.GetAttribute("Latitude")
            longitude = site.GetAttribute("Longitude")
            coordinates = f"Latitude: {latitude}, Longitude: {longitude}"

        # Disciplina de projeto (Arquitetura, Estrutura, Instalações)
        disciplines = []
        for element in model.by_type("IfcBuildingElement"):
            classification = element.IsDefinedBy
            if classification:
                for classification_rel in classification:
                    if classification_rel.is_a("IfcRelDefinesByProperties"):
                        pset = classification_rel.RelatingPropertyDefinition
                        if pset and hasattr(pset, "Discipline"):
                            disciplines.append(pset.Discipline)

        # Verifica elementos sobrepostos (se houver)
        overlaps = "No overlap detected"
        # (Adicione o código que verifica se há elementos sobrepostos, se disponível)

        # Verifica se especificações técnicas estão preenchidas
        specifications = "No specifications"
        for element in model.by_type("IfcElement"):
            pset = element.IsDefinedBy
            if pset:
                for p in pset:
                    if p.is_a("IfcPropertySet"):
                        if hasattr(p, "Specifications") and p.Specifications:
                            specifications = p.Specifications

        # Adiciona as informações ao relatório
        report["coordinates"] = coordinates
        report["disciplines"] = disciplines
        report["overlaps"] = overlaps
        report["specifications"] = specifications

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

    # Salva o relatório completo em TXT
    with open("validation_report.txt", "w") as txt_file:
        for report in validation_reports:
            txt_file.write(f"Arquivo: {report['file']}\n")
            if "error" in report:
                txt_file.write(f"  Erro: {report['error']}\n")
            else:
                txt_file.write(f"  Coordenadas: {report['coordinates']}\n")
                txt_file.write(f"  Disciplinas: {', '.join(report['disciplines'])}\n")
                txt_file.write(f"  Sobreposição: {report['overlaps']}\n")
                txt_file.write(f"  Especificações Técnicas: {report['specifications']}\n")
                for result in report["results"]:
                    txt_file.write(f"  Entidade: {result['entity']}, Status: {result['status']}\n")
            txt_file.write("\n")

if __name__ == "__main__":
    main()
