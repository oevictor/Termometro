import serial.tools.list_ports

# Lista todas as portas seriais
ports = serial.tools.list_ports.comports()
print(f"Portas seriais detectadas: {len(ports)}")
connected_devices = []

for port in ports:
    try:
        # Tenta abrir a porta para verificar se está disponível
        with serial.Serial(port.device) as ser:
            status = "Disponível"
    except serial.SerialException:
        # Caso a porta esteja em uso
        status = "Em uso"

    connected_devices.append({
        "device": port.device,
        "description": port.description,
        "hwid": port.hwid,
        "status": status
    })

# Exibe as informações das portas
if connected_devices:
    print("Portas seriais detectadas:")
    for device in connected_devices:
        print(f"Porta: {device['device']}, Descrição: {device['description']}, HWID: {device['hwid']}, Status: {device['status']}")
else:
    print("Nenhuma porta serial detectada.")



