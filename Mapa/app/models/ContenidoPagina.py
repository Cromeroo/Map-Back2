from app import db

class ContenidoPagina(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seccion = db.Column(db.String(50), nullable=False)  
    tipo = db.Column(db.String(20), nullable=False)    
    contenido = db.Column(db.Text, nullable=False)