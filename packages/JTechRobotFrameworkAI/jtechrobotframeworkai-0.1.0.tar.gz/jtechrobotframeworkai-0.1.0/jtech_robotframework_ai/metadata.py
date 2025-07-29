from typing import Dict, List, Any, Optional
import re

# Catálogo de metadados das tabelas
TABLE_CATALOG: Dict[str, Dict[str, Any]] = {
    "revenue_forecast": {
        "description": "Projeções e dados históricos de faturamento por cliente e período",
        "keywords": [
            "faturamento",
            "receita",
            "projeção",
            "previsão",
            "cliente",
            "resíduo",
        ],
    },
    "customer": {
        "description": "Dados cadastrais de clientes",
        "keywords": ["cliente", "contato", "cadastro", "empresa"],
    },
    # Adicione outras tabelas conforme necessário
}


def find_relevant_tables(query: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Encontra tabelas relevantes para uma consulta com base nas palavras-chave e descrições.

    Args:
        query: A consulta do usuário
        limit: Número máximo de tabelas a retornar

    Returns:
        Lista de tabelas relevantes ordenadas por relevância (mais relevante primeiro)
    """
    query_lower = query.lower()
    results = []

    for table_name, metadata in TABLE_CATALOG.items():
        score = 0

        # Pontua palavras-chave presentes na consulta
        for keyword in metadata.get("keywords", []):
            if keyword.lower() in query_lower:
                score += 10  # Palavras-chave têm maior peso

        # Pontua palavras da descrição presentes na consulta
        description = metadata.get("description", "")
        words = re.findall(r"\w+", description.lower())
        for word in words:
            if len(word) > 3 and word in query_lower:  # Ignora palavras muito curtas
                score += 5

        # Adiciona à lista de resultados se houver alguma relevância
        if score > 0:
            results.append(
                {
                    "table_name": table_name,
                    "score": score,
                    "description": description,
                    "keywords": metadata.get("keywords", []),
                }
            )

    # Ordena por relevância e limita o número de resultados
    return sorted(results, key=lambda x: x["score"], reverse=True)[:limit]


def get_table_metadata(table_name: str) -> Optional[Dict[str, Any]]:
    """
    Obtém os metadados de uma tabela específica.

    Args:
        table_name: Nome da tabela

    Returns:
        Metadados da tabela ou None se a tabela não estiver no catálogo
    """
    if table_name in TABLE_CATALOG:
        return {"table_name": table_name, **TABLE_CATALOG[table_name]}
    return None


def list_all_tables() -> List[Dict[str, Any]]:
    """
    Lista todas as tabelas do catálogo com seus metadados.

    Returns:
        Lista de todas as tabelas com metadados
    """
    return [
        {"table_name": table_name, **metadata}
        for table_name, metadata in TABLE_CATALOG.items()
    ]
