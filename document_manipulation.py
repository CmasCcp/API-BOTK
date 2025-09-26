import os
import requests

# Cargar plantilla base LaTeX
def load_template():
    template_path = os.getenv("LATEX_TEMPLATE_PATH", "report-structure.tex")
    try:
        with open(template_path, "r", encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"[load_template] ❌ Plantilla no encontrada: {template_path}")
        return ""

# Editar una sección del documento
def edit_section(template: str, section: str, content: str) -> str:
    placeholder = f"<<{section}>>"
    if placeholder not in template:
        print(f"[edit_section] ❗ MARCADOR NO ENCONTRADO: {placeholder}")
    else:
        print(f"[edit_section] ✅ Reemplazando {placeholder}")
    return template.replace(placeholder, content)

# Guardar documento actualizado
def save_updated_document(updated_template: str, output_file: str):
    with open(output_file, "w", encoding='utf-8') as file:
        file.write(updated_template)

# Actualizar una sección específica del documento
def update_latex_section(section_key: str, new_content: str, thread_id: str):
    file_path = f"generatedDocuments/{thread_id}.tex"
    marker = f"<<{section_key}>>"
    start_tag = f"% --- start:{section_key} ---"
    end_tag = f"% --- end:{section_key} ---"

    try:
        # Crear documento si no existe
        if not os.path.exists(file_path):
            os.makedirs("generatedDocuments", exist_ok=True)
            template = load_template()
            save_updated_document(template, file_path)
            print(f"[update_latex_section] 📄 Documento LaTeX creado para {thread_id}")

        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        updated_lines = []
        skip = False
        for line in lines:
            if start_tag in line:
                skip = True
                continue
            if end_tag in line:
                skip = False
                continue
            if skip:
                continue
            updated_lines.append(line)
            if marker in line:
                new_content = sanitize_latex_input(new_content)
                updated_lines.append(f"{start_tag}\n")
                updated_lines.append(new_content.strip() + "\n")
                updated_lines.append(f"{end_tag}\n")
                print(f"[edit_section] ✅ Reemplazado marcador {marker}")

        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(updated_lines)

        # Llamar a compilador
        requests.post("http://localhost:5001/compile", json={"thread_id": thread_id})
        print(f"[compile] ✅ Compilación solicitada para thread_id={thread_id}")

    except Exception as e:
        print(f"[update_latex_section] ⚠️ Error al actualizar sección {section_key}: {e}")

# Sanitiza texto para LaTeX
def sanitize_latex_input(text: str) -> str:
    replacements = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}'
    }

    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text
