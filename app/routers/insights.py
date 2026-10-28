from fastapi import APIRouter, Depends
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Transaction, User
from app.security import get_current_user
router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/monthly")
def monthly_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(
            func.strftime("%Y-%m", Transaction.date).label("month"),
            func.sum(
                case(
                    (Transaction.is_income.is_(True), Transaction.amount),
                    else_=0,
                )
            ).label("income"),
            func.sum(
                case(
                    (Transaction.is_income.is_(False), Transaction.amount),
                    else_=0,
                )
            ).label("expenses"),
        )
        .group_by("month")
        .order_by("month")
        .filter(Transaction.user_id == current_user.id)
        .all()
    )

    return [
        {
            "month": month,
            "income": float(income or 0),
            "expenses": float(expenses or 0),
            "net": float((income or 0) - (expenses or 0)),
        }
        for month, income, expenses in rows
    ]
@router.get("/categories")
def category_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(
            Category.name,
            func.sum(Transaction.amount).label("total"),
        )
        .join(Transaction, Transaction.category_id == Category.id)
        .filter(Transaction.user_id == current_user.id)
        .group_by(Category.name)
        .order_by(Category.name)
        .all()
    )

    return [
        {"category": name, "total": float(total)}
        for name, total in rows
    ]

@router.get("/unusual")
def unusual_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transactions = (
        db.query(Transaction)
        .filter(Transaction.category_id.isnot(None))
        .filter(Transaction.user_id == current_user.id)
        .all()
    )

    averages = {}
    for transaction in transactions:
        category_id = transaction.category_id
        averages.setdefault(category_id, []).append(transaction.amount)

    category_averages = {
        category_id: sum(amounts) / len(amounts)
        for category_id, amounts in averages.items()
    }

    flagged = []
    for transaction in transactions:
        average = category_averages[transaction.category_id]
        if transaction.amount > 2 * average:
            flagged.append({
                "id": transaction.id,
                "description": transaction.description,
                "amount": transaction.amount,
                "category_average": round(average, 2),
                "reason": "More than twice the average amount in this category",
            })

    return flagged
