document.addEventListener('DOMContentLoaded', () => {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(position => {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;

            const map = L.map('map').setView([latitude, longitude], 15);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: 'Map data © OpenStreetMap contributors'
            }).addTo(map);

            const userMarker = L.marker([latitude, longitude]).addTo(map)
                .bindPopup('Você está aqui')
                .openPopup();

            fetch('/buscar_lojas', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ latitude: latitude, longitude: longitude })
            })
            .then(response => response.json())
            .then(lojas => {
                const lista = document.getElementById('lista-lojas');
                lojas.forEach(loja => {
                    const div = document.createElement('div');
                    div.className = 'loja';
                    div.innerHTML = `<b>${loja.nome}</b> - ${loja.desconto}% de desconto<br>Promoção: ${loja.descricao}<br><br>`;
                    lista.appendChild(div);

                    L.marker([loja.latitude, loja.longitude])
                        .addTo(map)
                        .bindPopup(`<b>${loja.nome}</b><br>${loja.desconto}% OFF<br>${loja.descricao}`);
                });
            });

        }, () => {
            alert('Não foi possível obter sua localização.');
        });
    } else {
        alert('Geolocalização não suportada pelo navegador.');
    }
});
