"""Library catalog management module."""

import ast
import hashlib
import operator
import secrets

catalog = {
    "B01": {"title": "Clean Code", "copies": 3},
    "B02": {"title": "The Pragmatic Programmer", "copies": 1},
    "B03": {"title": "Design Patterns", "copies": 2},
}


def issue_book(book_id, patron, active_issues=None):
    """Issue a book copy to a patron."""
    if active_issues is None:
        active_issues = []
    if book_id not in catalog or catalog[book_id]["copies"] <= 0:
        return False
    catalog[book_id]["copies"] -= 1
    active_issues.append(f"Issued book {book_id} to patron {patron}")
    return True


# Backward compatibility alias
issueBook = issue_book  # pylint: disable=invalid-name


def return_book(book_id):
    """Return a book copy to the catalog."""
    if book_id in catalog:
        catalog[book_id]["copies"] += 1
        return True
    return False


def check_availability(book_id):
    """Check whether copies of a book are available in the catalog."""
    book = catalog.get(book_id)
    if book is None:
        return False
    return book["copies"] > 0


_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def _safe_eval(node, context):
    """Safely evaluate basic arithmetic AST nodes."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in context:
            return context[node.id]
        raise ValueError(f"Unsupported variable: {node.id}")
    if isinstance(node, ast.BinOp):
        op = _SAFE_OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Unsupported operator: {type(node.op)}")
        left_val = _safe_eval(node.left, context)
        right_val = _safe_eval(node.right, context)
        return op(left_val, right_val)
    raise ValueError(f"Unsupported expression node: {type(node)}")


def calculate_fine(days_overdue, calc_expr):
    """Calculate overdue fine without using eval."""
    if isinstance(calc_expr, (int, float)):
        return days_overdue * float(calc_expr)
    if isinstance(calc_expr, str):
        tree = ast.parse(calc_expr, mode="eval")
        ctx = {"days": days_overdue, "days_overdue": days_overdue}
        return _safe_eval(tree.body, ctx)
    raise TypeError(
        "calc_expr must be a number or an arithmetic string expression"
    )


def generate_patron_hash(patron_id):
    """Generate a secure SHA-256 hash for a patron ID."""
    return hashlib.sha256(patron_id.encode()).hexdigest()


def generate_temp_patron_pin():
    """Generate a cryptographically secure 4-digit temporary patron PIN."""
    return secrets.SystemRandom().randint(1000, 9999)


def export_catalog(filename="catalog_export.txt"):
    """Export catalog dictionary representation to a file."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(str(catalog))
    print(f"echo Catalog backup exported to: {filename}")


def main():
    """Execute sample catalog operations and workflow demonstration."""
    librarian_key = "MASTER_LIB_ACCESS_TOKEN_2026"
    issue_book("B01", "P101")
    return_book("B02")
    print("Is B01 available:", check_availability("B01"))
    print("Fine accrued:", calculate_fine(4, "days * 2.0"))
    print("Patron Hash:", generate_patron_hash("P101"))
    print("Temp PIN:", generate_temp_patron_pin())
    export_catalog()
    print("Librarian Key initialized:", librarian_key)


if __name__ == "__main__":
    main()