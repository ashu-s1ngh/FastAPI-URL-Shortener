import secrets
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from database import engine, SessionLocal, get_db
import models, schemas
from sqlalchemy.orm import Session
from security import hash_password, verify_password, create_access_token, get_current_user, oauth2_scheme
from fastapi.security import OAuth2PasswordRequestForm

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener API")

def generate_short_url(length: int = 6) -> str:
    return secrets.token_urlsafe(length)[0:6]

@app.post("/urls/", response_model=schemas.URLResponse)
def create_url(url: schemas.URLCreate,current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if url.custom_code:
        existing_url = db.query(models.URLItem).filter(models.URLItem.short_url == url.custom_code).first()
        if existing_url:
            raise HTTPException(status_code=400, detail="Custom shortcode already in use.")
        short_url = url.custom_code
    else:
        short_url = generate_short_url()

    expires_at = None
    if url.expires_in_minutes:
        future_time = datetime.now(timezone.utc) + timedelta(minutes=url.expires_in_minutes)
        expires_at = future_time.replace(tzinfo=None)

    db_url = models.URLItem(
        original_url=str(url.original_url),
        short_url=short_url,
        expires_at=expires_at,
        owner_id = current_user.id
    )

    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    return db_url

@app.get("/my-urls/", response_model=list[schemas.URLResponse])
def get_my_urls(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    urls = db.query(models.URLItem).filter(models.URLItem.owner_id == current_user.id).all()
    return urls

@app.get("/{short_url}")
def redirect_to_original(short_url: str, db: Session = Depends(get_db)):
    db_url = db.query(models.URLItem).filter(models.URLItem.short_url == short_url).first()

    if not db_url:
        raise HTTPException(status_code=404, detail="Short URL not found.")

    if db_url.expires_at:
        db_time = db_url.expires_at

        if db_time.tzinfo is None:
            db_time = db_time.replace(tzinfo=timezone.utc)

        if db_time < datetime.now(timezone.utc):
            raise HTTPException(status_code=410, detail="This short URL has expired.")

    db_url.clicks += 1
    db.commit()

    return RedirectResponse(url=db_url.original_url)

@app.get("/analytics/{short_url}", response_model=schemas.URLResponse)
def get_url_analytics(short_url: str, db: Session = Depends(get_db)):
    db_url = db.query(models.URLItem).filter(models.URLItem.short_url == short_url).first()
    if db_url is None:
        raise HTTPException(status_code=404, detail="URL not found.")

    return db_url


@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(models.User).filter((models.User.username == user.username) | (models.User.email == user.email)).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered.")
    
    hashed_password = hash_password(user.password)
    
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    print(f"DEBUG USER FROM DB -> Username: {db_user.username}, Email: {db_user.email}")
    
    return db_user

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password.", headers={"WWW-Authenticate": "Bearer"})
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.delete("/urls/{short_url}")
def delete_url(short_url: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_url = db.query(models.URLItem).filter(models.URLItem.short_url == short_url).first()
    
    if not db_url:
        raise HTTPException(status_code=404, detail="Short URL not found.")
    
    if db_url.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this URL.")
    
    db.delete(db_url)
    db.commit()
    
    return {"detail": "URL deleted successfully."}

@app.post("/logout")
def logout(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    already_blacklisted = db.query(models.BlacklistedToken).filter(models.BlacklistedToken.token == token).first()
    if already_blacklisted:
        return {"detail": "Token is already blacklisted."}
    
    blacklisted_token = models.BlacklistedToken(token=token)
    db.add(blacklisted_token)
    db.commit()
    
    return {"detail": "Successfully logged out."}