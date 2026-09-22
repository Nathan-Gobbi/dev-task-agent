"""Command-line interface for the Dev Task Agent."""

from src.graph import build_graph
from src.state import AgentState


def main() -> None:
    print("================================")
    print("       DEV TASK AGENT")
    print("================================")
    task = input("\nDescreva sua tarefa:\n> ").strip()
    if not task:
        print("A tarefa não pode estar vazia.")
        return

    initial_state: AgentState = {
        "task": task,
        "analysis": "",
        "plan": "",
        "review": "",
        "approved": False,
        "revision_count": 0,
        "max_revisions": 2,
        "revision_limit_reached": False,
    }

    print("\nAnalisando tarefa...")
    print("Gerando plano...")
    print("Revisando plano...")
    result = build_graph().invoke(initial_state)

    status = "APROVADO" if result["approved"] else "NÃO APROVADO"
    if result["revision_limit_reached"]:
        status += " (LIMITE DE REVISÕES ATINGIDO)"

    print("\nResultado")
    print("---------")
    print(f"\nAnálise:\n{result['analysis']}")
    print(f"\nPlano:\n{result['plan']}")
    print(f"\nRevisão:\n{result['review']}")
    print(f"\nStatus: {status}")
    print(f"\nRevisões realizadas: {result['revision_count']}")


if __name__ == "__main__":
    main()
