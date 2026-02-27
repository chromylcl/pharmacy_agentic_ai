from langchain.tools import Tool


# MOCK FUNCTIONS (temporary until teammates push code)

def search_medicine(query: str):
    return f"[MOCK] Medicine search result for: {query}"


def create_order(data: str):
    return f"[MOCK] Order created for: {data}"


medicine_tool = Tool(
    name="MedicineSearch",
    func=search_medicine,
    description="Search medicines in pharmacy inventory",
)

order_tool = Tool(
    name="CreateOrder",
    func=create_order,
    description="Create a medicine order",
)

TOOLS = [medicine_tool, order_tool]