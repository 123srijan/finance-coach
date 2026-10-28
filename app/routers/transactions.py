from datetime import date
from io import BytesIO


import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Transaction, User
from app.schemas import TransactionCreate, TransactionResponse
from app.security import get_current_user

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=TransactionResponse)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_transaction = Transaction(**transaction.model_dump(), user_id=current_user.id)
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction
@router.get("/", response_model=list[TransactionResponse])
def list_transactions(
    start_date: date | None = None,
    end_date: date | None = None,
    category_id: int | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Transaction).filter(Transaction.user_id == current_user.id)

    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    if category_id is not None:
        query = query.filter(Transaction.category_id == category_id)
    if search:
        query = query.filter(Transaction.description.ilike(f"%{search}%"))

    return query.order_by(Transaction.date.desc()).all()

@router.patch("/{transaction_id}/category")
def set_transaction_category(
    transaction_id: int,
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.user_id == current_user.id,
    ).first()
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    transaction.category_id = category_id
    db.commit()
    db.refresh(transaction)

    return {
        "id": transaction.id,
        "description": transaction.description,
        "category_id": transaction.category_id,
    }


@router.post("/import")
async def import_transactions(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file")

    try:
        contents = await file.read()
        df = pd.read_csv(BytesIO(contents))

        required_columns = {"date", "description", "amount", "category_id"}
        missing = required_columns - set(df.columns)
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing CSV columns: {', '.join(sorted(missing))}",
            )

        imported = 0
        for _, row in df.iterrows():
            category_id = (
                None if pd.isna(row["category_id"]) else int(row["category_id"])
            )
            if category_id is not None:
                category = db.query(Category).filter(Category.id == category_id).first()
                if category is None:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Category {category_id} does not exist",
                    )

            db.add(
                Transaction(
                    date=date.fromisoformat(str(row["date"])),
                    description=str(row["description"]),
                    amount=float(row["amount"]),
                    category_id=category_id,
                    user_id=current_user.id,
                )
            )
            imported += 1

        db.commit()
        return {"imported": imported}

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Could not read CSV: {exc}")
