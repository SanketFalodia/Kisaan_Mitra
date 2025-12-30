def generate_form(required_fields):
    return [
        {
            "field_name": field,
            "question": f"{field.replace('_', ' ').title()} बताइए"
        }
        for field in required_fields
    ]