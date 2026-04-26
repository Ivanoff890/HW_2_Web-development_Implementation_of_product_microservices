from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import requests
import models, schemas, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Order Service")

PRODUCT_SERVICE_URL = "http://localhost:8001/products"


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_product_exists(product_id: int):
    try:
        response = requests.get(f"{PRODUCT_SERVICE_URL}/{product_id}")
        return response.status_code == 200, response.json() if response.status_code == 200 else None
    except:
        return False, None


@app.post("/orders", response_model=schemas.OrderResponse)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    exists, product = check_product_exists(order.product_id)
    if not exists:
        raise HTTPException(status_code=404, detail="Product not found")

    if product["stock"] < order.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")

    total_price = product["price"] * order.quantity
    db_order = models.Order(
        product_id=order.product_id,
        quantity=order.quantity,
        total_price=total_price,
        status="pending"
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


@app.get("/orders", response_model=List[schemas.OrderResponse])
def get_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).all()


@app.get("/orders/{order_id}", response_model=schemas.OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.put("/orders/{order_id}/status", response_model=schemas.OrderResponse)
def update_status(order_id: int, status_update: schemas.OrderUpdateStatus, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status_update.status
    db.commit()
    db.refresh(order)
    return order