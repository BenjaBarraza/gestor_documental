import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:url_launcher/url_launcher.dart';
import '../services/api_service.dart';
import 'document_viewer_screen.dart';

class DocumentListScreen extends StatefulWidget {
  const DocumentListScreen({super.key});

  @override
  State<DocumentListScreen> createState() => _DocumentListScreenState();
}

class _DocumentListScreenState extends State<DocumentListScreen> {
  List documentos = [];
  bool loading = true;
  String error = '';

  @override
  void initState() {
    super.initState();
    fetchDocumentos();
  }

  Future<void> fetchDocumentos() async {
    setState(() {
      loading = true;
      error = '';
    });

    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access');
    final url = Uri.parse('${ApiService.baseUrl}/documentos/');

    try {
      final res = await http.get(
        url,
        headers: {'Authorization': 'Bearer $token'},
      );

      if (res.statusCode == 200) {
        final List decoded = jsonDecode(res.body);
        setState(() {
          documentos = decoded;
          loading = false;
        });
      } else {
        setState(() {
          error = 'Error ${res.statusCode}: ${res.reasonPhrase}';
          loading = false;
        });
      }
    } catch (e) {
      setState(() {
        error = 'Error de red: $e';
        loading = false;
      });
    }
  }

  Future<void> _eliminarDocumento(int id) async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access');
    final url = Uri.parse('${ApiService.baseUrl}/documentos/$id/eliminar/');

    final res = await http.delete(
      url,
      headers: {'Authorization': 'Bearer $token'},
    );

    if (res.statusCode == 204) {
      setState(() {
        documentos.removeWhere((doc) => doc['id'] == id);
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Documento eliminado')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Error al eliminar el documento')),
      );
    }
  }

  Future<void> _confirmarEliminacion(int id) async {
    final confirm = await showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('¿Eliminar documento?'),
        content: const Text('Esta acción no se puede deshacer.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('Cancelar')),
          ElevatedButton(onPressed: () => Navigator.pop(context, true), child: const Text('Eliminar')),
        ],
      ),
    );

    if (confirm == true) {
      await _eliminarDocumento(id);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Mis documentos'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Recargar',
            onPressed: fetchDocumentos,
          ),
        ],
      ),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : error.isNotEmpty
              ? Center(child: Text(error, style: const TextStyle(color: Colors.redAccent)))
              : documentos.isEmpty
                  ? const Center(child: Text('No hay documentos subidos aún'))
                  : ListView.builder(
                      itemCount: documentos.length,
                      itemBuilder: (context, index) {
                        final doc = documentos[index];
                        return ListTile(
                          leading: const Icon(Icons.insert_drive_file),
                          title: Text(doc['nombre']),
                          subtitle: Text('Tamaño: ${doc['size'] ?? 0} KB'),
                          onTap: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => DocumentViewerScreen(
                                  nombre: doc['nombre'],
                                  url: doc['archivo'],
                                ),
                              ),
                            );
                          },
                          trailing: IconButton(
                            icon: const Icon(Icons.delete, color: Colors.redAccent),
                            onPressed: () => _confirmarEliminacion(doc['id']),
                          ),
                        );
                      },
                    ),
    );
  }
}
