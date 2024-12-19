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
                for result in report["results"]:
                    txt_file.write(f"  Entidade: {result['entity']}, Status: {result['status']}\n")
            txt_file.write("\n")

if __name__ == "__main__":
    def main():
    # Carrega o IDS
    try:
        with open(IDS_PATH, "r") as f:
            ids_root = etree.parse(f).getroot()
        print(f"IDS carregado com sucesso de {IDS_PATH}.")
    except Exception as e:
        print(f"Erro ao carregar o IDS: {e}")
        return

    # Valida todos os arquivos IFC no repositório
    validation_reports = []
    ifc_files = [file for file in os.listdir(".") if file.endswith(".ifc")]
    if not ifc_files:
        print("Nenhum arquivo IFC encontrado no diretório.")
        return

    print(f"Arquivos IFC encontrados: {ifc_files}")
    for file in ifc_files:
        try:
            report = validate_ifc_with_ids(file, ids_root)
            validation_reports.append(report)
            print(f"Validação concluída para o arquivo: {file}")
        except Exception as e:
            print(f"Erro ao validar o arquivo {file}: {e}")

    # Salva o relatório completo em JSON
    try:
        with open(REPORT_PATH, "w") as report_file:
            json.dump(validation_reports, report_file, indent=4)
        print(f"Relatório JSON salvo em: {REPORT_PATH}")
    except Exception as e:
        print(f"Erro ao salvar o relatório JSON: {e}")

    # Salva o relatório completo em TXT
    try:
        with open("validation_report.txt", "w") as txt_file:
            for report in validation_reports:
                txt_file.write(f"Arquivo: {report['file']}\n")
                if "error" in report:
                    txt_file.write(f"  Erro: {report['error']}\n")
                else:
                    for result in report["results"]:
                        txt_file.write(f"  Entidade: {result['entity']}, Status: {result['status']}\n")
                txt_file.write("\n")
        print("Relatório TXT salvo em: validation_report.txt")
    except Exception as e:
        print(f"Erro ao salvar o relatório TXT: {e}")

