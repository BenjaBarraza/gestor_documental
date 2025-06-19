import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:url_launcher/url_launcher.dart';
import '../services/api_service.dart';

class DocumentViewerScreen extends StatelessWidget {
  final String nombre;
  final String url;

  const DocumentViewerScreen({
    super.key,
    required this.nombre,
    required this.url,
  });

  bool esImagen(String ruta) {
    return ruta.endsWith('.png') || ruta.endsWith('.jpg') || ruta.endsWith('.jpeg');
  }

  bool esTexto(String ruta) {
    return ruta.endsWith('.txt') || ruta.endsWith('.log');
  }

  bool esArchivoExterno(String ruta) {
    return ruta.endsWith('.pdf') || ruta.endsWith('.docx') || ruta.endsWith('.xlsx');
  }

  @override
  Widget build(BuildContext context) {
    final fullUrl = url.startsWith('http')
        ? url
        : '${ApiService.baseUrl.replaceFirst('/api', '')}$url';

    return Scaffold(
      appBar: AppBar(title: Text(nombre)),
      body: esImagen(url)
          ? Center(child: Image.network(fullUrl))
          : esTexto(url)
              ? FutureBuilder(
                  future: http.read(Uri.parse(fullUrl)),
                  builder: (context, snapshot) {
                    if (snapshot.connectionState == ConnectionState.waiting) {
                      return const Center(child: CircularProgressIndicator());
                    } else if (snapshot.hasError) {
                      return const Center(child: Text('Error al cargar el archivo'));
                    } else {
                      return SingleChildScrollView(
                        padding: const EdgeInsets.all(16),
                        child: SelectableText(
                          snapshot.data ?? '',
                          style: const TextStyle(fontSize: 16),
                        ),
                      );
                    }
                  },
                )
              : esArchivoExterno(url)
                  ? Center(
                      child: ElevatedButton.icon(
                        icon: const Icon(Icons.open_in_new),
                        label: const Text('Abrir documento'),
                        onPressed: () async {
                          final Uri urlToOpen = Uri.parse(fullUrl);
                          if (!await launchUrl(urlToOpen, mode: LaunchMode.externalApplication)) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('No se pudo abrir el documento')),
                            );
                          }
                        },
                      ),
                    )
                  : const Center(child: Text('Tipo de archivo no compatible')),
    );
  }
}
