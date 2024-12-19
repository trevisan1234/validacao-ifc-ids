def validate_ifc_with_ids(ifc_file, ids_root):
    """Valida um arquivo IFC contra o IDS fornecido."""
    report = {"file": ifc_file, "results": []}
    
    try:
        # Abre o arquivo IFC
        print(f"Processando arquivo: {ifc_file}")  # Mensagem de debug
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

        # Adiciona os resultados no relatório
        result = {
            "IfcProject": "Presente" if ifc_project else "Ausente",
            "IfcBuilding": "Presente" if ifc_building else "Ausente",
            "IfcBuildingStorey": "Presente" if ifc_building_storey else "Ausente",
            "IfcSpace": f"{len(ifc_space)} espaços encontrados" if len(ifc_space) >= 2 else "Menos de 2 espaços encontrados",
            "Coordenadas": coordinates,
            "Disciplinas": disciplines,
            "Especificações Técnicas": technical_specifications,
        }
        
        # Verificando se os dados foram coletados
        print(f"Resultado para {ifc_file}: {result}")  # Mensagem de debug
        report["results"].append(result)
    
    except Exception as e:
        report["error"] = str(e)
        print(f"Erro ao processar o arquivo {ifc_file}: {e}")  # Mensagem de erro
    
    # Verificando se algum resultado foi adicionado à lista
    if not report["results"]:
        print(f"A lista 'results' está vazia para o arquivo: {ifc_file}")  # Mensagem de debug
    
    return report
