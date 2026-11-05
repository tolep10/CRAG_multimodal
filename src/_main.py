from typing import Optional, Dict, Any

from langgraph.graph.state import CompiledStateGraph

from mmcrag_graph import MMCRAGGraph



def get_workflow() -> Optional[CompiledStateGraph]:
    graph = MMCRAGGraph()

    return graph.get_grap_workflow()


def test(app_graph: CompiledStateGraph, query: str) -> None:
    initial_state = {
        "query": query,
        "retry_count": 1,
    }

    final_state: Dict[str, Any] = app_graph.invoke(initial_state)
    generation = final_state.get("generation", {})

    if generation.get("images"):
        print(f"Imagenes: {generation['images']}")
    if generation.get("content"):
        print(f"Contenido: {generation['content']}")


def main(app_graph: CompiledStateGraph) -> None:
    try:
        while True:
            query = input("Tu:> ")

            if not query or not query.strip():
                continue

            if query.lower() in ("bye", "quit", "exit", "adios"):
                break

            try:
                print("Obteniendo respuesta...\n\n")
                test(app_graph, query)
            except Exception as e:
                print(f"Error procesando la consulta: {e}")

            print(f"\n\n")

    except  Exception as e:
        print(f"Ocurrió un error en el main: {e}")


if __name__ == "__main__":
    _app_graph = get_workflow()

    if not _app_graph:
        print("No se pudo obtener el workflow")
    else:
        main(_app_graph)
