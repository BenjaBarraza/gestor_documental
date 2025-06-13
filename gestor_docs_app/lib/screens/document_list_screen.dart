import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:url_launcher/url_launcher.dart';
import 'document_viewer_screen.dart';
import '../services/api_service.dart';

class DocumentListScreen extends StatefulWidget {
  const DocumentListScreen({super.key});

  @override
  State<DocumentListScreen> createState() => _DocumentListScreenState();
}

class _DocumentListScreenState extends State<DocumentListScreen> {
  List documentos = [];
  bool loading = true;
  String? error;

  @override
  void initState() {
    super.initState();
    fetchDocumentos();
  }

  Future<void> fetchDocumentos() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access');
    


    if (token == null) {
      setState(() {
        error = 'No has iniciado sesión.';
        loading = false;
      });
      return;
    }

    final url = Uri.parse('${ApiService.baseUrl}/documentos/');
    print('URL final: ${ApiService.baseUrl}/documentos/');


    
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
      } else if (res.statusCode == 401) {
        await prefs.clear();
        if (!mounted) return;
        Navigator.pushReplacementNamed(context, '/login');
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

  Future<void> _abrirDocumento(String ruta) async {
    final Uri url = Uri.parse('http://localhost:8000$ruta');
    if (!await launchUrl(url, mode: LaunchMode.externalApplication)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No se pudo abrir el documento')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Mis documentos')),
      body: loading
          ? const Center(child: CircularProgressIndicator())
          : error != null
              ? Center(child: Text(error!, style: const TextStyle(color: Colors.redAccent)))
              : documentos.isEmpty
                  ? const Center(child: Text('Aún no tienes documentos.'))
                  : ListView.builder(
                      itemCount: documentos.length,
                      itemBuilder: (context, index) {
                        final doc = documentos[index];
                        return ListTile(
                          leading: const Icon(Icons.insert_drive_file),
                          title: Text(doc['nombre']),
                          subtitle: Text('Tamaño: ${doc['size']} KB'),
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
                        );
                      },
                    ),
    );
  }
}
