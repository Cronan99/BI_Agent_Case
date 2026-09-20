import os
from datetime import date

from dotenv import load_dotenv
from google import genai
from google.genai import types
from sqlalchemy.orm import Session

from .. import models
from .tools import (sales_summary_tool,
                     top_products_tool,
                     sales_breakdown_tool,
                     sales_trend_tool,)


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not configured")

client = genai.Client(api_key=GEMINI_API_KEY)

MODEL = "gemini-3.5-flash"


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

sales_breakdown_declaration = types.FunctionDeclaration(
    name="get_sales_breakdown",
    description=(
        "Get sales grouped by brand, category, region, or city for the "
        "authenticated user's accessible brands. Use this when the user "
        "asks how sales are distributed or wants to compare sales between "
        "brands, categories, regions, or cities."
    ),
    parameters={
        "type": "object",
        "properties": {
            "group_by": {
                "type": "string",
                "enum": [
                    "brand",
                    "category",
                    "region",
                    "city",
                ],
                "description": "Dimension to group the sales by.",
            },
            "start_date": {
                "type": "string",
                "description": "Start date in YYYY-MM-DD format.",
            },
            "end_date": {
                "type": "string",
                "description": "End date in YYYY-MM-DD format.",
            },
        },
        "required": ["group_by"],
    },
)

sales_trend_declaration = types.FunctionDeclaration(
    name="get_sales_trend",
    description=(
        "Get sales over time for the authenticated user's accessible brands. "
        "Use this when the user asks how sales have developed, changed, "
        "or trended over time."
    ),
    parameters={
        "type": "object",
        "properties": {
            "granularity": {
                "type": "string",
                "enum": ["week", "month"],
                "description": (
                    "Time interval used to group sales. "
                    "Use month by default unless weekly detail is requested."
                ),
            },
            "start_date": {
                "type": "string",
                "description": "Start date in YYYY-MM-DD format.",
            },
            "end_date": {
                "type": "string",
                "description": "End date in YYYY-MM-DD format.",
            },
        },
    },
)

sales_tools = types.Tool(
    function_declarations=[
        sales_summary_declaration,
        top_products_declaration,
        sales_breakdown_declaration,
        sales_trend_declaration,
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

    if function_call.name == "get_sales_breakdown":
        return sales_breakdown_tool(
            db=db,
            current_user=current_user,
            group_by=args["group_by"],
            start_date=parse_date(args.get("start_date")),
            end_date=parse_date(args.get("end_date")),
        )

    if function_call.name == "get_sales_trend":
        return sales_trend_tool(
            db=db,
            current_user=current_user,
            granularity=args.get("granularity", "month"),
            start_date=parse_date(args.get("start_date")),
            end_date=parse_date(args.get("end_date")),
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
            "The available sales data covers January 2025 through June 2026. "
            "Answer questions using the available sales tools. "
            "Never invent sales numbers. "
            "Never invent dates or time periods that the user did not specify. "
            "If the user's requested time period is ambiguous, ask for clarification. "
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

    max_tool_calls = 4

    for _ in range(max_tool_calls):
        response = client.models.generate_content(
            model=MODEL,
            contents=contents,
            config=config,
        )

        if not response.function_calls:
            return response.text

        contents.append(
            response.candidates[0].content
        )

        function_response_parts = []

        for function_call in response.function_calls:
            tool_result = execute_tool(
                function_call=function_call,
                db=db,
                current_user=current_user,
            )

            function_response_parts.append(
                types.Part.from_function_response(
                    name=function_call.name,
                    response={"result": tool_result},
                )
            )

        contents.append(
            types.Content(
                role="user",
                parts=function_response_parts,
            )
        )

    raise RuntimeError(
        "Agent exceeded maximum number of tool calls"
    )