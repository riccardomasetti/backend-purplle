from app import create_app, db
from app.models.models import Project, Milestone  # Se sono in models/models.py
# Alternativa: from app.models import Project, Milestone  # Se sono direttamente in models.py

app = create_app()

with app.app_context():
    try:
        # Trova il progetto di test
        test_project = Project.query.filter_by(title="Progetto di Test").first()

        if test_project:
            print(f"Trovato progetto di test: {test_project.id} - {test_project.title}")

            # Trova tutte le milestone associate
            milestones = Milestone.query.filter_by(project_id=test_project.id).all()
            print(f"Trovate {len(milestones)} milestone associate")

            # Elimina prima le milestone (per evitare vincoli di chiave esterna)
            for milestone in milestones:
                print(f"Eliminazione milestone: {milestone.title}")
                db.session.delete(milestone)

            # Poi elimina il progetto
            print(f"Eliminazione progetto: {test_project.title}")
            db.session.delete(test_project)

            # Commit delle modifiche
            db.session.commit()
            print("Dati di test eliminati dal database.")
        else:
            print("Nessun progetto di test trovato.")
    except Exception as e:
        print(f"Si è verificato un errore: {str(e)}")
        db.session.rollback()  # Rollback in caso di errore
