import os
import json
import django

# 1. Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MathWeb.settings')
django.setup()

from MainApp.models import Problem, Bundle, DifTag# Ajusta si tus modelos están en otra app
from UsersApp.models import User

def import_data():
    with open('legacy.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Pillamos al primer superusuario que encontremos para ser el "nuevo autor"
    nuevo_autor = User.objects.filter(is_superuser=True).first()
    
    if not nuevo_autor:
        print("❌ Error: No hay ningún superusuario en la DB. Crea uno primero.")
        return

    print(f"✅ Usando a {nuevo_autor.email} como autor de rescate.")

    for entry in data:
        model_name = entry['model']
        fields = entry['fields']
        pk = entry['pk']

        # Separamos la lógica según el modelo
        if model_name == 'MainApp.problem':
            obj, created = Problem.objects.get_or_create(
                id=pk,
                defaults={
                    'title': fields.get('title'),
                    'text': fields.get('text'),
                    'author': nuevo_autor, # Forzamos el nuevo autor
                    'dif_tag': DifTag.objects.get(id=fields.get('dif_tag')-19),
                    'likes_count': 0
                }
            )
            # Gestionar ManyToMany (type_tags)
            if 'type_tags' in fields:
                obj.type_tags.set(fields['type_tags'])
            
            status = "Creado" if created else "Ya existía"
            print(f"Problem {pk}: {status}")

        elif model_name == 'MainApp.bundle':
            # Repetimos lógica para Bundles
            obj, created = Bundle.objects.get_or_create(
                id=pk,
                defaults={
                    'title': fields.get('title', 'Sin título'),
                    'description': fields.get('description', ''),
                    'author': nuevo_autor,
                    'likes_count': 0
                }
            )
            if 'problems' in fields:
                obj.problems.set(fields['problems'])
            print(f"Bundle {pk}: {'Creado' if created else 'Ya existía'}")

    print("\n🚀 Proceso finalizado. ¡Datos rescatados!")

if __name__ == '__main__':
    import_data()