import os
import json
import django

# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MathWeb.settings')
django.setup()

from MainApp.models import Problem, TypeTag, DifTag

def repair_tags_and_difficulties():

        
    # 2. Cargar el JSON para vincular
    try:
        with open('backup_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ No se encontró el archivo JSON.")
        return

    print("🔗 Vinculando tags a los problemas existentes...")

    for item in data:
        if item['model'] == 'MainApp.typetag':
            pk = item['pk']
            fields = item['fields']
            TypeTag.objects.get_or_create(id=pk, defaults=fields)
        elif item['model'] == "MainApp.diftag":
            DifTag.objects.get_or_create(id=pk, defaults=fields)

    print("\n🚀 ¡Sincronización completada!")

if __name__ == '__main__':
    repair_tags_and_difficulties()