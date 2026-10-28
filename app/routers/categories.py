from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.models import Category

router = APIRouter(prefix="/categories", tags=["categories"])

DEFAULT_CATEGORIES = [
    "Food",
    "Shopping",
    "Travel",
    "Transport",
    "Housing",
    "Utilities",
    "Healthcare",
    "Education",
    "Entertainment",
    "Personal care",
    "Groceries",
    "Other",
]


def add_default_categories(db: Session) -> None:
    existing_names = {
        name.lower()
        for (name,) in db.query(Category.name).all()
    }

    for name in DEFAULT_CATEGORIES:
        if name.lower() not in existing_names:
            db.add(Category(name=name))

    db.commit()


@router.post("/")
def create_category(name: str, db: Session = Depends(get_db)):
    name = name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Category name cannot be empty")

    existing = db.query(Category).filter(Category.name.ilike(name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")

    category = Category(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/")
def list_categories(db: Session = Depends(get_db)):
    add_default_categories(db)
    return db.query(Category).order_by(Category.name).all()



@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()
    return {"message": f"Category '{category.name}' deleted"}