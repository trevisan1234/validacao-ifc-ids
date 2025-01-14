import os
import json
import csv
from lxml import etree
import ifcopenshell
import pyproj

# Função para verificar se uma entidade é suportada no esquema IFC
def is_field_supported(schema, field):
    schema_fields = {
        "IFC2X3": [
            "IfcWall", "IfcSlab", "IfcWindow", "IfcDoor", "IfcBeam", "IfcColumn", "IfcStair",
            "IfcRoof", "IfcPile", "IfcFooting", "IfcCovering"
        ],
        "IFC4": [
            "IfcWall", "IfcSlab", "IfcWindow", "IfcDoor", "IfcBeam", "IfcColumn", "IfcStair",
            "IfcRoof", "IfcPile", "IfcFooting", "IfcElectricGenerator", "IfcTransformer",
            "IfcUninterruptiblePowerSupply", "IfcCableSegment", "IfcPump", "IfcTank", 
            "IfcWaterHeater", "IfcCovering"
        ]
    }
    return field in schema_fields.get(schema, [])

try:
    print("ifcopenshell importado com sucesso!")
except ImportError as e:
    print(f"Erro ao importar ifcopenshell: {str(e)}")
    exit(1)

# Caminhos para os arquivos de relatório diretamente no diretório raiz
IDS_PATH = "./ids.xsd"
TXT_REPORT_PATH = "./validation_report.txt"
JSON_REPORT_PATH = "./validation_report.json"
CSV_REPORT_PATH = "./validation_report.csv"

additional_fields = [
    "IfcWall", "IfcSlab", "IfcWindow", "IfcDoor", "IfcBeam", "IfcColumn", "IfcStair", "IfcRoof",
    "IfcPile",  # Elementos de concreto armado em fundações profundas
    "IfcFooting",  # Elementos de concreto armado em fundações rasas
    "IfcElectricGenerator", "IfcTransformer", "IfcUninterruptiblePowerSupply",  # Instalações elétricas de alto custo
    "IfcCableSegment",  # Condutores de energia elétrica
    "IfcPump", "IfcTank", "IfcWaterHeater",  # Instalações hidráulicas/sanitárias de alto custo
    "IfcCovering"  # Elementos de impermeabilização
]

# Função para validar a presença dos campos no arquivo IFC
def validate_ifc_with_ids(file, ids_root):
    try:
        ifc_file = ifcopenshell.open(file)

        # Campos básicos
        project = ifc_file.by_type("IfcProject")
        building = ifc_file.by_type("IfcBuilding")
        
        # Obter valores principais de IfcProject
        project_content = project[0].Name if project and hasattr(project[0], "Name") else 0

        # Obter valores principais de IfcBuilding
        building_content = building[0].Name if building and hasattr(building[0], "Name") else 0
        building_storey = ifc_file.by_type("IfcBuildingStorey") or []
        storey_count = len(building_storey)
        spaces = ifc_file.by_type("IfcSpace")
        coordinates = get_coordinates(ifc_file)
        
        # Obter o esquema do arquivo IFC
        schema = ifc_file.schema.lower()  # Retorna "ifc2x3" ou "ifc4" (normalmente em minúsculas)

        # Filtrar os campos adicionais com base no esquema
        supported_fields = [field for field in additional_fields if is_field_supported(schema.upper(), field)]

        # Conta os elementos dos campos adicionais suportados
        additional_data = {}
        for field in supported_fields:
            entities = ifc_file.by_type(field)
            additional_data[field] = len(entities) if entities else 0


        # Identificar os campos ignorados
        ignored_fields = [field for field in additional_fields if field not in supported_fields]


        result = {
            "file": file,
            "results": [{
                "IfcProject": project_content,
                "IfcBuilding": building_content,
                "IfcBuildingStorey": storey_count,
                "IfcSpace": len(spaces) if spaces else 0,
                "Latitude": coordinates["Latitude"],
                "Longitude": coordinates["Longitude"],
                "Elevação": coordinates["Elevação"],
                "IgnoredFields": {field: schema.upper() for field in ignored_fields}  # Campos ignorados e seus esquemas
            }]
        }

        # Adiciona os campos adicionais
        for field, count in additional_data.items():
            result["results"][0][field] = count

        # Adiciona o endereço postal
        postal_address = get_postal_address(ifc_file)
        result["results"][0]["IfcPostalAddress"] = postal_address

        # Atualiza o resultado para armazenar IgnoredFields como lista clara
        result["results"][0]["IgnoredFields"] = [
            {"Field": field, "Schema": schema.upper()} for field in ignored_fields
        ]
        
        return result
    except Exception as e:
        result = {
            "file": file,
            "results": [{
                "IfcProject": 0,
                "IfcBuilding": 0,
                "IfcBuildingStorey": 0,
                "IfcSpace": 0,
                "Latitude": 0,
                "Longitude": 0,
                "Elevação": 0,
                "IfcPostalAddress": "Erro ao processar endereço",
                "IgnoredFields": [],
            }]
        }
        # Preencher os campos adicionais com 0
        for field in additional_fields:
            result["results"][0][field] = 0

        # Adicionar a mensagem de erro no resultado
        result["error"] = f"Erro ao processar {file}: {str(e)}"

        return result

# Função para obter coordenadas em formato legível
def get_coordinates(ifc_file):
    try:
        ifc_site = ifc_file.by_type("IfcSite")
        if ifc_site:
            site = ifc_site[0]
            if hasattr(site, "RefLatitude") and hasattr(site, "RefLongitude"):
                lat = site.RefLatitude
                lon = site.RefLongitude
                elevation = getattr(site, "RefElevation", "0.0")
                return {
                    "Latitude": latitude_to_decimal(lat),
                    "Longitude": longitude_to_decimal(lon),
                    "Elevação": elevation
                }
    except Exception as e:
        return {"Latitude": 0, "Longitude": 0, "Elevação": 0}
    return {"Latitude": 0, "Longitude": 0, "Elevação": 0}

# Funções para conversão de latitude/longitude
def latitude_to_decimal(lat):
    if len(lat) >= 3:  # Verifica se há pelo menos 3 valores
        return sum(x / 60 ** i for i, x in enumerate(lat)) if lat else "Inválido"
    return 0  # Retorna 0 como valor padrão

def longitude_to_decimal(lon):
    if len(lon) >= 3:  # Verifica se há pelo menos 3 valores
        return sum(x / 60 ** i for i, x in enumerate(lon)) if lon else "Inválido"
    return 0  # Retorna 0 como valor padrão

# Verifica o campo IfcPostalAddress
def get_postal_address(ifc_file):
    try:
        addresses = ifc_file.by_type("IfcPostalAddress")
        if addresses:
            address = addresses[0]
            address_lines = getattr(address, "AddressLines", [])
            postal_code = getattr(address, "PostalCode", "Não especificado")
            city = getattr(address, "Town", "Não especificado")
            return f"{', '.join(address_lines)}, {city}, CEP: {postal_code}" if address_lines else "Endereço não especificado"
    except Exception as e:
        return f"Erro ao processar endereço: {str(e)}"
    return "Endereço não encontrado"

# Função principal
def main():
    print("Iniciando a validação e geração de relatórios...")

    if not os.access('.', os.W_OK):
        print(f"Não é possível escrever no diretório atual ({os.getcwd()}). Verifique as permissões.")
        return  # Finaliza o programa se não puder escrever
    else:
        print("Permissão de escrita confirmada.")

    # Carrega o IDS
    with open(IDS_PATH, "r") as f:
        ids_root = etree.parse(f).getroot()

    # Valida todos os arquivos IFC no diretório
    validation_reports = []
    for file in os.listdir("."):
        if file.endswith(".ifc"):
            try:
                print(f"Validando: {file}")
                validation_reports.append(validate_ifc_with_ids(file, ids_root))
            except Exception as e:
                validation_reports.append({"file": file, "error": f"Erro inesperado: {str(e)}"})

    # Salva o relatório JSON
    print("Salvando relatório JSON...")
    with open(JSON_REPORT_PATH, "w") as json_file:
        json.dump(validation_reports, json_file, indent=4)

    # Salva o relatório TXT
    print("Salvando relatório TXT...")
    with open(TXT_REPORT_PATH, "w") as txt_file:
        for report in validation_reports:
            txt_file.write(f"Arquivo: {report['file']}\n")
            if "error" in report:
                txt_file.write(f"  Erro: {report['error']}\n")
                for key, value in report["results"][0].items():
                    if key not in ["IgnoredFields", "IfcPostalAddress"]:  # Ignorar campos especiais por enquanto
                        txt_file.write(f"    {key}: {value}\n")
                    elif key == "IgnoredFields":
                        for field_info in value:  # value é uma lista de dicionários
                            txt_file.write(f"    {field_info['Field']}: não suportado no esquema {field_info['Schema']}\n")
                    elif key == "IfcPostalAddress":
                        txt_file.write(f"  Endereço: {value}\n")

            else:
                for result in report["results"]:
                    for key, value in result.items():
                        # Escreve as coordenadas de forma separada (Latitude, Longitude, Elevação)
                        if key in ["Latitude", "Longitude", "Elevação"]:
                            txt_file.write(f"    {key}: {value}\n")
                        elif key == "IfcPostalAddress":
                            txt_file.write(f"  Endereço: {value}\n")
                        if key == "IgnoredFields":
                            for field_info in value:  # value é uma lista de dicionários
                                txt_file.write(f"    {field_info['Field']}: não suportado no esquema {field_info['Schema']}\n")
                        else:
                            txt_file.write(f"    {key}: {value}\n")

    # Salva o relatório CSV
    print("Salvando relatório CSV...")
    with open(CSV_REPORT_PATH, "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        headers = ["Arquivo", "IfcProject", "IfcBuilding", "IfcBuildingStorey", "IfcSpace", "Latitude", "Longitude", "Elevação", "IfcPostalAddress", "IgnoredFields"] + additional_fields
        csv_writer.writerow(headers)
        for report in validation_reports:
            if "error" in report:
                row = [report["file"], 0, 0, 0, 0, 0, 0, 0, "Erro ao processar", ""]
                row.extend(0 for _ in additional_fields)
                csv_writer.writerow(row)

            else 
                for result in report["results"]:
                    row = [report["file"]]
                    row.extend(result.get(field, 0) for field in [
                    "IfcProject", "IfcBuilding", "IfcBuildingStorey", "IfcSpace",
                    "Latitude", "Longitude", "Elevação", "IfcPostalAddress"
                    ])
                    ignored_fields_str = "; ".join([f"{field['Field']} ({field['Schema']})" for field in result.get("IgnoredFields", [])])
                    row.append(ignored_fields_str)
                    row.extend(result.get(field, 0) for field in additional_fields)
                    csv_writer.writerow(row)

if __name__ == "__main__":
    main()
