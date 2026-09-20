import os
from datetime import date

from dotenv import load_dotenv
from google import genai
from google.genai import types
from sqlalchemy.orm import Session

from .. import models
from .tools import sales_summary_tool, top_products_tool


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured")

client = genai.Client(api_key=GEMINI_API_KEY)

MODEL = "gemini-3.8-flash"


sales_summary_declaration = types.FunctionDeclaration(
    name="get_sales_summary",
    description=(
        "Get aggregated sales statistics for the authenticated user's "
        "accessible brands. Use this when the user asks about revenue, "
        "units sold, or number of orders."
    ),
    parameters={
        "type": "object",
        "properties": {
            "start_date": {
                "type": "string",
                "description": "Start date in YYYY-MM-DD format.",
            },
            "end_date": {
                "type": "string",
                "description": "End date in YYYY-MM-DD format.",
            },
            "region": {
                "type": "string",
                "description": "Swedish region to filter by.",
            },
            "city": {
                "type": "string",
                "description": "City to filter by.",
            },
        },
    },
)

top_products_declaration = types.FunctionDeclaration(
    name="get_top_products",
    description=(
        "Get the top-selling products for the authenticated user's "
        "accessible brands. Use this when the user asks which products "
        "perform best or generate the most revenue."
    ),
    parameters={
        "type": "object",
        "properties": {
            "limit": {
                "type": "integer",
                "description": "Number of top products to return. Default is 5.",
            },
            "start_date": {
                "type": "string",
                "description": "Start date in YYYY-MM-DD format.",
            },
            "end_date": {
                "type": "string",
                "description": "End date in YYYY-MM-DD format.",
            },
            "region": {
                "type": "string",
                "description": "Swedish region to filter by.",
            },
            "city": {
                "type": "string",
                "description": "City to filter by.",
            },
        },
    },
)

sales_tools = types.Tool(
    function_declarations=[
        sales_summary_declaration,
        top_products_declaration,
        ]
)


def parse_date(value: str | None) -> date | None:
    if value is None:
        return None

    return date.fromisoformat(value)


def execute_tool(
    function_call,
    db: Session,
    current_user: models.User,
):
    args = function_call.args

    if function_call.name == "get_sales_summary":
        return sales_summary_tool(
            db=db,
            current_user=current_user,
            start_date=parse_date(args.get("start_date")),
            end_date=parse_date(args.get("end_date")),
            region=args.get("region"),
            city=args.get("city"),
        )

    if function_call.name == "get_top_products":
        return top_products_tool(
            db=db,
            current_user=current_user,
            limit=args.get("limit", 5),
            start_date=parse_date(args.get("start_date")),
            end_date=parse_date(args.get("end_date")),
            region=args.get("region"),
            city=args.get("city"),
        )

    raise ValueError(
        f"Unknown tool: {function_call.name}"
    )


def ask_agent(
    message: str,
    db: Session,
    current_user: models.User,
) -> str:

    config = types.GenerateContentConfig(
        system_instruction=(
            "You are a sales insights assistant. "
            "Answer questions using the available sales tools. "
            "Never invent sales numbers. "
            "All numerical sales facts must come from tool results. "
            "If the available data cannot answer the question, "
            "clearly explain that. "
            "Answer in the same language as the user."
        ),
        tools=[sales_tools],
        automatic_function_calling=
            types.AutomaticFunctionCallingConfig(
                disable=True
            ),
    )

    contents = [
        types.Content(
            role="user",
            parts=[types.Part(text=message)],
        )
    ]

    response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=config,
    )

    if not response.function_calls:
        return response.text

    function_call = response.function_calls[0]

    # Execute tools server-side with the authenticated user context.
    tool_result = execute_tool(
        function_call=function_call,
        db=db,
        current_user=current_user,
    )

    contents.append(response.candidates[0].content)

    function_response = types.Part.from_function_response(
        name=function_call.name,
        response={"result": tool_result},
    )

    contents.append(
        types.Content(
            role="user",
            parts=[function_response],
        )
    )

    final_response = client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=config,
    )

    return final_response.text