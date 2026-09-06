"""Anthropic tool-use schemas mirroring the MCP tools in main.py.

These are used only by the standalone chatbot.py for local natural-language
testing. When Claude talks to the real FastMCP server it discovers tools
directly via the MCP protocol -- this file exists so the same intent ->
tool -> parameters pipeline can be exercised without an MCP client.
"""

TOOLS = [
    {
        "name": "add_family_member",
        "description": "Add a new family member to track expenses/income for.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "relationship": {"type": "string", "description": "e.g. Self, Father, Mother, Brother, Sister"},
            },
            "required": ["name", "relationship"],
        },
    },
    {
        "name": "list_family_members",
        "description": "List all registered family members.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "add_expense",
        "description": (
            "Record that a family member spent money. Infer the category from context "
            "if not stated (e.g. Food, Petrol, Transport, Rent, Utilities, Entertainment, "
            "Health, Shopping, Education, Travel, Other)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "member_name": {"type": "string"},
                "amount": {"type": "number", "description": "Amount in INR"},
                "category": {"type": "string"},
                "expense_date": {"type": "string", "description": "YYYY-MM-DD, 'today', or 'yesterday'"},
                "description": {"type": "string"},
            },
            "required": ["member_name", "amount", "category"],
        },
    },
    {
        "name": "list_expenses",
        "description": "List expenses, optionally filtered by family member, category, or date range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "member_name": {"type": "string"},
                "category": {"type": "string"},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"},
                "limit": {"type": "integer"},
            },
        },
    },
    {
        "name": "update_expense",
        "description": "Update an existing expense by id.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expense_id": {"type": "integer"},
                "amount": {"type": "number"},
                "category": {"type": "string"},
                "expense_date": {"type": "string"},
                "description": {"type": "string"},
            },
            "required": ["expense_id"],
        },
    },
    {
        "name": "delete_expense",
        "description": "Delete an expense by id.",
        "input_schema": {
            "type": "object",
            "properties": {"expense_id": {"type": "integer"}},
            "required": ["expense_id"],
        },
    },
    {
        "name": "add_income",
        "description": "Record income received by a family member.",
        "input_schema": {
            "type": "object",
            "properties": {
                "member_name": {"type": "string"},
                "amount": {"type": "number", "description": "Amount in INR"},
                "source": {"type": "string", "description": "e.g. Salary, Freelance, Gift, Interest"},
                "income_date": {"type": "string"},
                "notes": {"type": "string"},
            },
            "required": ["member_name", "amount", "source"],
        },
    },
    {
        "name": "list_income",
        "description": "List income records, optionally filtered by family member or date range.",
        "input_schema": {
            "type": "object",
            "properties": {
                "member_name": {"type": "string"},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"},
                "limit": {"type": "integer"},
            },
        },
    },
    {
        "name": "update_income",
        "description": "Update an existing income record by id.",
        "input_schema": {
            "type": "object",
            "properties": {
                "income_id": {"type": "integer"},
                "amount": {"type": "number"},
                "source": {"type": "string"},
                "income_date": {"type": "string"},
                "notes": {"type": "string"},
            },
            "required": ["income_id"],
        },
    },
    {
        "name": "delete_income",
        "description": "Delete an income record by id.",
        "input_schema": {
            "type": "object",
            "properties": {"income_id": {"type": "integer"}},
            "required": ["income_id"],
        },
    },
    {
        "name": "total_income",
        "description": "Get total income, optionally for a specific family member.",
        "input_schema": {"type": "object", "properties": {"member_name": {"type": "string"}}},
    },
    {
        "name": "total_expenses",
        "description": "Get total expenses, optionally for a specific family member.",
        "input_schema": {"type": "object", "properties": {"member_name": {"type": "string"}}},
    },
    {
        "name": "current_balance",
        "description": "Get current balance (income minus expenses), optionally for a specific family member.",
        "input_schema": {"type": "object", "properties": {"member_name": {"type": "string"}}},
    },
    {
        "name": "expenses_by_category",
        "description": "Get total expenses grouped by category, optionally for one family member.",
        "input_schema": {"type": "object", "properties": {"member_name": {"type": "string"}}},
    },
    {
        "name": "expenses_by_member",
        "description": "Get total expenses grouped by family member, optionally filtered by category.",
        "input_schema": {"type": "object", "properties": {"category": {"type": "string"}}},
    },
    {
        "name": "monthly_income",
        "description": "Get total income for a given month, e.g. month='August'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "month": {"type": "string"},
                "year": {"type": "integer"},
                "member_name": {"type": "string"},
            },
        },
    },
    {
        "name": "monthly_expenses",
        "description": "Get total expenses for a given month, e.g. month='August'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "month": {"type": "string"},
                "year": {"type": "integer"},
                "member_name": {"type": "string"},
            },
        },
    },
    {
        "name": "monthly_summary",
        "description": "Get income, expenses, and balance for a given month.",
        "input_schema": {
            "type": "object",
            "properties": {
                "month": {"type": "string"},
                "year": {"type": "integer"},
                "member_name": {"type": "string"},
            },
        },
    },
    {
        "name": "compare_months",
        "description": "Compare income, expenses, and balance between two months, e.g. month_a='July', month_b='August'.",
        "input_schema": {
            "type": "object",
            "properties": {
                "month_a": {"type": "string"},
                "month_b": {"type": "string"},
                "year_a": {"type": "integer"},
                "year_b": {"type": "integer"},
                "member_name": {"type": "string"},
            },
            "required": ["month_a", "month_b"],
        },
    },
    {
        "name": "set_budget",
        "description": "Set (or update) the monthly budget for a category.",
        "input_schema": {
            "type": "object",
            "properties": {
                "category": {"type": "string"},
                "amount": {"type": "number"},
            },
            "required": ["category", "amount"],
        },
    },
    {
        "name": "list_budgets",
        "description": "List all configured budgets.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "budget_status",
        "description": "Get budget vs. actual spend status for a category, or all categories if omitted.",
        "input_schema": {"type": "object", "properties": {"category": {"type": "string"}}},
    },
    {
        "name": "financial_insights",
        "description": (
            "Get financial insights: income, expenses, balance, top spending category, "
            "savings rate, and personalized suggestions."
        ),
        "input_schema": {"type": "object", "properties": {"member_name": {"type": "string"}}},
    },
]
