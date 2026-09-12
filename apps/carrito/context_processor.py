def total_carrito(request):
    total = 0
    if "carrito" in request.session:
        for key, value in request.session["carrito"].items():
            total += int(value.get("acumulado", 0))  # Manejo de valores faltantes
            
    return {"total_boleta": total}
