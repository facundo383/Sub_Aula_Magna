import qrcode

# Dirección IP fija basada en los datos de tu adaptador Wi-Fi
ip_local = "10.0.48.97"
puerto = 8501
network_url = f"http://{ip_local}:{puerto}"

print(f"🌍 Tu Network URL es: {network_url}")

# Generar QR
qr = qrcode.QRCode(version=1, box_size=10, border=4)
qr.add_data(network_url)
qr.make(fit=True)

imagen_qr = qr.make_image(fill_color="black", back_color="white")
imagen_qr.save("codigo_qr_local.png")

print("----------------------------------------------------------------")
print("¡Listo! Se creó 'codigo_qr_local.png'.")
print("Asegúrate de que tu celular esté conectado al MISMO Wi-Fi que la PC.")
print("----------------------------------------------------------------")